import schedule
import time
import threading
from datetime import datetime
from src.models.account import ManusAccount, db
from src.services.manus_service import ManusService

class AccountScheduler:
    def __init__(self, app):
        self.app = app
        self.running = False
        self.scheduler_thread = None
    
    def sync_all_accounts(self):
        """Sync all accounts - called by scheduler"""
        with self.app.app_context():
            print(f"[{datetime.now()}] Starting scheduled account sync...")
            
            accounts = ManusAccount.query.all()
            
            for account in accounts:
                try:
                    print(f"Syncing account: {account.email}")
                    
                    manus_service = ManusService()
                    password = account.get_password()
                    
                    if not password:
                        print(f"No password found for {account.email}")
                        account.status = 'error'
                        continue
                    
                    success, session_data, error_msg = manus_service.refresh_session(
                        account.email, 
                        password, 
                        account.get_session_data()
                    )
                    
                    if success:
                        account.status = 'active'
                        account.last_login = datetime.utcnow()
                        account.set_session_data(session_data)
                        print(f"Successfully synced {account.email}")
                    else:
                        account.status = 'error'
                        print(f"Failed to sync {account.email}: {error_msg}")
                    
                    account.updated_at = datetime.utcnow()
                    
                except Exception as e:
                    print(f"Error syncing {account.email}: {str(e)}")
                    account.status = 'error'
                    account.updated_at = datetime.utcnow()
            
            try:
                db.session.commit()
                print(f"[{datetime.now()}] Scheduled sync completed for {len(accounts)} accounts")
            except Exception as e:
                print(f"Error committing changes: {str(e)}")
                db.session.rollback()
    
    def run_scheduler(self):
        """Run the scheduler in a separate thread"""
        print("Account scheduler started")
        
        # Schedule daily sync at midnight
        schedule.every().day.at("00:00").do(self.sync_all_accounts)
        
        # For testing purposes, also schedule every 5 minutes (comment out in production)
        # schedule.every(5).minutes.do(self.sync_all_accounts)
        
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
        
        print("Account scheduler stopped")
    
    def start(self):
        """Start the scheduler"""
        if not self.running:
            self.running = True
            self.scheduler_thread = threading.Thread(target=self.run_scheduler)
            self.scheduler_thread.daemon = True
            self.scheduler_thread.start()
            print("Scheduler started successfully")
    
    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        print("Scheduler stopped")
    
    def trigger_manual_sync(self):
        """Trigger a manual sync immediately"""
        thread = threading.Thread(target=self.sync_all_accounts)
        thread.daemon = True
        thread.start()
        return "Manual sync triggered"

