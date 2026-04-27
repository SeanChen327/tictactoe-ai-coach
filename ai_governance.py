# ai_governance.py
import time
import re
from typing import Dict, Any, List, Tuple
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class GomokuAIGovernance:
    """
    Validation and Assurance module based on the AI Periodic Table.
    Covers: Guardrails (Gr), Red Teaming (Rt) mitigation, Metrics (Mt), Evaluation (Ev), and Human-in-the-Loop (Hl).
    """

    def __init__(self):
        self.board_size = 15
        self.cost_per_1k_tokens = 0.0001 
        self.human_review_threshold = 0.7 
        
        # [SECURITY UPGRADE] Enhanced adversarial patterns
        # 1. Catches traditional jailbreaks
        # 2. Catches system prompt spoofing (e.g., [ROLE]:, [CONTEXT]:)
        self.adversarial_patterns = re.compile(
            r"(ignore previous|system prompt|bypass|jailbreak|forget instructions|\[ROLE\]:|\[STRICT GUIDELINES\]:|\[TACTICAL ANALYSIS\]:)", 
            re.IGNORECASE
        )

    # --- Validation: Input Guardrails & Red Teaming Mitigation (Gr/Rt) ---
    def detect_adversarial_input(self, user_message: str) -> bool:
        """
        [Red Teaming / Guardrails] Validates incoming user messages against known injection patterns.
        
        Args:
            user_message (str): The raw input from the user.
            
        Returns:
            bool: True if malicious/adversarial intent is detected, False otherwise.
        """
        if self.adversarial_patterns.search(user_message):
            logger.warning(f"[Rt/Gr] Adversarial input detected and blocked: {user_message}")
            return True
        return False

    # --- Validation: Output Guardrails (Gr) ---
    def validate_output_safety(self, ai_reply: str, board: List[str]) -> Tuple[bool, str]:
        """
        [Guardrails] Runtime safety and policy filter.
        Checks for coordinate hallucinations and enforces the strict word count policy.
        
        Returns:
            Tuple[bool, str]: (Is Safe, Reason/Error Message)
        """
        # 1. Policy Enforcement: Word Count Limit (< 80 words)
        word_count = len(ai_reply.split())
        if word_count > 80:
            logger.warning(f"[Gr] Policy violation: Output too long ({word_count} words).")
            return False, "Output exceeded the 80-word limit policy."

        # 2. Hallucination Detection: Coordinate Validation
        coords = re.findall(r'[A-Z]\d+', ai_reply.upper())
        if not coords:
            return True, "Safe" 
        
        for coord in coords:
            match = re.match(r'([A-Z]+)(\d+)', coord)
            if not match:
                continue
                
            col_str, row_str = match.groups()
            
            if len(col_str) > 1:
                logger.warning(f"[Gr] Out-of-bounds coordinate: {coord}")
                return False, f"Invalid coordinate {coord}"
                
            col = ord(col_str) - ord('A')
            row = int(row_str) - 1
            
            if row < 0 or row >= self.board_size or col < 0 or col >= self.board_size:
                logger.warning(f"[Gr] Out-of-bounds coordinate: {coord}")
                return False, f"Invalid coordinate {coord}"
                
            idx = row * self.board_size + col
            if board[idx] != "":
                logger.warning(f"[Gr] Occupied position hallucinated: {coord}")
                return False, f"Coordinate {coord} is already occupied"
                
        return True, "Safe"

    # --- Assurance: Metrics (Mt) ---
    def track_telemetry(self, start_time: float, response_text: str) -> Dict[str, Any]:
        """
        [Metrics] Basic measurements: latency, estimated tokens, and cost.
        """
        latency = time.time() - start_time
        estimated_tokens = len(response_text) * 2 
        estimated_cost = (estimated_tokens / 1000) * self.cost_per_1k_tokens
        
        return {
            "latency_ms": round(latency * 1000, 2),
            "estimated_tokens": estimated_tokens,
            "estimated_cost": f"${estimated_cost:.6f}",
            "timestamp": datetime.utcnow().isoformat()
        }

    # --- Assurance: Evaluation (Ev) & Human-in-the-Loop (Hl) ---
    def evaluate_response_consistency(self, ai_reply: str, last_evaluation: Dict[str, Any]) -> float:
        """
        [Evaluation] Quality audit comparing AI reply to deterministic heuristics.
        """
        if not last_evaluation or "win_rate" not in last_evaluation:
            return 1.0 

        match = re.search(r'(\d+)%', ai_reply)
        if match:
            reported_wr = int(match.group(1))
            actual_wr = int(last_evaluation["win_rate"].replace('%', ''))
            
            deviation = abs(reported_wr - actual_wr)
            return max(0.0, 1.0 - (deviation / 100))
            
        return 0.5 

    def requires_human_oversight(self, quality_score: float) -> bool:
        """
        [Human-in-the-Loop] Flags low-quality interactions for manual review.
        
        Args:
            quality_score (float): The score returned by the Evaluation function.
            
        Returns:
            bool: True if it should be flagged for HITL, False otherwise.
        """
        escalate = quality_score < self.human_review_threshold
        if escalate:
            logger.info(f"[Hl] Interaction flagged for Human-in-the-Loop review. Score: {quality_score}")
        return escalate