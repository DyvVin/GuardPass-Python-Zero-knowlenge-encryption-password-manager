from database.connection import get_db_connection

class PasswordAuditor:
    
    @staticmethod
    def run_security_audit() -> dict:

        metrics = {                     #### for renovation
            "total_accounts": 0,
            "weak_passwords": 0,        #### for renovation
            "reused_passwords": 0,     
            "security_score": 100      
        }
        
        with get_db_connection() as conn:
            row = conn.execute("SELECT COUNT(*) as total FROM accounts;").fetchone()
            metrics["total_accounts"] = row["total"] if row else 0
            
            if metrics["total_accounts"] == 0:
                return metrics
                
            row_weak = conn.execute("SELECT COUNT(*) as weak FROM accounts WHERE password_length < 8;").fetchone()
            metrics["weak_passwords"] = row_weak["weak"] if row_weak else 0
            
            dup_query = """
                SELECT SUM(cnt) as reused_total FROM (
                    SELECT COUNT(*) as cnt 
                    FROM accounts 
                    GROUP BY password_hash_md5 
                    HAVING COUNT(*) > 1
                );
            """
            row_dup = conn.execute(dup_query).fetchone()
            metrics["reused_passwords"] = row_dup["reused_total"] if row_dup["reused_total"] else 0
            
            penalty = (metrics["weak_passwords"] * 15) + (metrics["reused_passwords"] * 10)
            metrics["security_score"] = max(0, 100 - penalty)
            
            return metrics
