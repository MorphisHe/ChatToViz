import re

class MessageManager:
    def __init__(self):
        self.message_history = []
        self.regex_pattern = r"```python\n(.*?)```"

    def get_message_history(self):
        return self.message_history
    
    def get_last_response(self):
        return self.message_history[-1]["content"]
    
    def get_clean_code(self, message):
        '''
        code return by chatgpt is wrapper by ```python ```
        '''
        return re.findall(self.regex_pattern, message, re.DOTALL)[0]
    
    def append(self, message, role="user"):
        self.message_history.append(
            {
                "role": role,
                "content": message
            }
        )