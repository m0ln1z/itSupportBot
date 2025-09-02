from openai import OpenAI
import asyncio
from typing import Dict, List
import re
from datetime import datetime

from app.config import settings

class ChatbotService:
    """Сервис для работы с ИИ чат-ботом"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None
        self.knowledge_base = self._load_knowledge_base()
    
    def _load_knowledge_base(self) -> Dict[str, str]:
        """Загрузка базы знаний для стандартных ответов"""
        return {
            "password": """
Для сброса пароля:
1. Перейдите на страницу https://password-reset.company.com
2. Введите ваш рабочий email
3. Проверьте почту и следуйте инструкциям
4. Если письмо не пришло, проверьте папку "Спам"
5. При проблемах обратитесь к системному администратору

Требования к паролю:
- Минимум 8 символов
- Должен содержать заглавные и строчные буквы
- Должен содержать цифры
- Должен содержать специальные символы
            """,
            
            "access": """
Для получения доступа к папке:
1. Определите полный путь к нужной папке
2. Обратитесь к вашему руководителю для подтверждения необходимости доступа
3. Отправьте заявку через ServiceDesk с указанием:
   - Полного пути к папке
   - Типа доступа (чтение/запись)
   - Бизнес-обоснования
4. Ожидайте обработки заявки (обычно 1-2 рабочих дня)
            """,
            
            "documents": """
Для отправки документов:
1. Используйте корпоративную систему документооборота
2. Убедитесь, что документ в поддерживаемом формате (PDF, DOC, DOCX)
3. Проверьте размер файла (максимум 10 МБ)
4. Укажите получателей и тему
5. При необходимости установите уровень конфиденциальности

Если документ не отправляется:
- Проверьте интернет-соединение
- Убедитесь, что файл не поврежден
- Попробуйте уменьшить размер файла
            """,
            
            "connection": """
Проблемы с подключением:
1. Проверьте кабель Ethernet или Wi-Fi соединение
2. Перезагрузите сетевое оборудование
3. Проверьте настройки прокси-сервера
4. Убедитесь, что антивирус не блокирует соединение
5. Попробуйте подключиться к другой сети

Для VPN подключения:
- Используйте корпоративный VPN клиент
- Введите ваши учетные данные
- При проблемах обратитесь к сетевому администратору
            """,
            
            "software": """
Установка программного обеспечения:
1. Проверьте список разрешенного ПО в корпоративном каталоге
2. Подайте заявку через ServiceDesk
3. Укажите бизнес-обоснование для установки
4. Дождитесь одобрения от ИТ-службы
5. ПО будет установлено удаленно или вам будут предоставлены инструкции

Обновление ПО происходит автоматически через корпоративную систему управления.
            """
        }
    
    async def get_response(self, message: str, user_id: str = "anonymous") -> str:
        """Получение ответа от ИИ"""
        try:
            # Классифицируем сообщение
            category = self.classify_message(message)
            
            # Если есть готовый ответ в базе знаний, используем его
            if category in self.knowledge_base:
                base_answer = self.knowledge_base[category]
                # Используем ИИ для персонализации ответа
                system_prompt = f"""
Ты - помощник ИТ-поддержки. У тебя есть стандартный ответ на вопрос пользователя, 
но ты должен адаптировать его под конкретный вопрос, сделать более персональным и дружелюбным.

Стандартный ответ: {base_answer}

Ответь на русском языке, будь вежливым и профессиональным.
"""
            else:
                system_prompt = """
Ты - опытный специалист ИТ-поддержки в российской компании. 
Твоя задача - помочь пользователям решить их технические проблемы.

Отвечай:
- На русском языке
- Кратко и по существу
- С пошаговыми инструкциями когда это необходимо
- Профессионально и дружелюбно

Если не можешь решить проблему, предложи обратиться к специалисту ИТ-поддержки.
"""
            
            if not self.client:
                return self._get_fallback_response(message)
                
            response = self.client.chat.completions.create(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"Ошибка при обращении к OpenAI: {e}")
            return self._get_fallback_response(message)
    
    def classify_message(self, message: str) -> str:
        """Классификация сообщения по категориям"""
        message_lower = message.lower()
        
        password_keywords = ["пароль", "password", "забыл", "сброс", "reset", "войти", "логин"]
        access_keywords = ["доступ", "папка", "файл", "права", "разрешение", "access", "folder"]
        document_keywords = ["документ", "отправить", "файл", "прикрепить", "загрузить", "document"]
        connection_keywords = ["подключение", "интернет", "сеть", "vpn", "wi-fi", "wifi", "connection"]
        software_keywords = ["программа", "установить", "обновить", "софт", "приложение", "software"]
        
        if any(keyword in message_lower for keyword in password_keywords):
            return "password"
        elif any(keyword in message_lower for keyword in access_keywords):
            return "access"
        elif any(keyword in message_lower for keyword in document_keywords):
            return "documents"
        elif any(keyword in message_lower for keyword in connection_keywords):
            return "connection"
        elif any(keyword in message_lower for keyword in software_keywords):
            return "software"
        else:
            return "general"
    
    def _get_fallback_response(self, message: str) -> str:
        """Резервный ответ если ИИ недоступен"""
        category = self.classify_message(message)
        
        if category in self.knowledge_base:
            return f"Вот информация по вашему вопросу:\n\n{self.knowledge_base[category]}"
        
        return """
Извините, в данный момент я не могу обработать ваш запрос. 
Пожалуйста, обратитесь к специалисту ИТ-поддержки:

📧 Email: it-support@company.com
📞 Телефон: +7 (495) 123-45-67
🕐 Рабочие часы: Пн-Пт 9:00-18:00

Или оставьте заявку в ServiceDesk системе.
        """
