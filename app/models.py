from sqlalchemy import Column, Integer, String, Index, CheckConstraint
from .database import Base


class Dish(Base):
    __tablename__ = "dishes"

    # ---------------------------
    # Primary Key
    # ---------------------------
    id = Column(Integer, primary_key=True, index=True)

    # ---------------------------
    # Dish Name
    # ---------------------------
    # Unique + indexed for fast lookup
    name = Column(String, unique=True, nullable=False, index=True)

    # ---------------------------
    # Business Fields
    # ---------------------------

    # Orders not yet completed
    pending = Column(Integer, default=0, nullable=False)

    # Created-till-now (Produced)
    completed = Column(Integer, default=0, nullable=False)

    # Predicted demand
    predicted = Column(Integer, default=0, nullable=False)

    # ---------------------------
    # Constraints (IMPORTANT)
    # ---------------------------
    __table_args__ = (
        # Prevent negative values (data integrity)
        CheckConstraint("pending >= 0", name="check_pending_non_negative"),
        CheckConstraint("completed >= 0", name="check_completed_non_negative"),
        CheckConstraint("predicted >= 0", name="check_predicted_non_negative"),

        # Extra index for scaling (faster searches)
        Index("idx_dish_name_unique", "name"),
    )

    # ---------------------------
    # Helper Methods (Optional but smart)
    # ---------------------------

    def total(self):
        """
        Total processed + pending workload
        Useful for status calculation
        """
        return self.pending + self.completed

    def status(self):
        """
        Returns computed status (optional backend logic)
        """
        total = self.total()

        if self.predicted == 0:
            return "NO DATA"
        elif total < self.predicted:
            return "OK"
        elif total == self.predicted:
            return "LIMIT"
        else:
            return "OVERLOAD"