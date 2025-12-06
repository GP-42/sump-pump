#! /usr/bin/python3

import keyring

class KeyRing:
    @staticmethod
    def get_service() -> str:
        return "sump-pump"
    
    @staticmethod
    def get_password(username) -> str:
        return keyring.get_password(KeyRing.get_service(), username)
    
    @staticmethod
    def set_password(username, password) -> bool:
        try:
            keyring.set_password(KeyRing.get_service(), username, password)
            return True
        except:
            return False