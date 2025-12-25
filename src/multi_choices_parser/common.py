class End:
    def __repr__(self) -> str:
        return "End"
    
    def __lt__(self, other) -> bool:
        return False
    
    def __gt__(self, other) -> bool:
        return True
    
    def __eq__(self, value: object) -> bool:
        return False
    
    def __hash__(self) -> int:
        return id(self)

DEFAULT_END_SYMB = End()

class ParserError(Exception):
    pass