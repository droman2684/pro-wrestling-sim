from dataclasses import dataclass

@dataclass
class Contract:
    """Represents a wrestler's contract."""
    per_appearance_fee: int = 1000 # Default fee

    def to_dict(self) -> dict:
        return {"per_appearance_fee": self.per_appearance_fee}

@dataclass
class Company:
    """Represents the player's company."""
    bank_account: int = 500000 # Starting money
    prestige: int = 50 # Starting prestige
    viewers: int = 1_000_000 # Starting weekly viewership

    def to_dict(self) -> dict:
        return {
            "bank_account": self.bank_account,
            "prestige": self.prestige,
            "viewers": self.viewers
        }
