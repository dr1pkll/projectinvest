class Solution:
    def isValid(self, s: str) -> bool:  
        for i in range(len(s)-1):
            if s[i] == s[i+1]:
                return True
            else:
                False