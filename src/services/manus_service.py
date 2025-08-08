import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from datetime import datetime

class ManusService:
    def __init__(self):
        self.driver = None
        self.wait = None
    
    def setup_driver(self, headless=True):
        """Setup Chrome driver with appropriate options"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)
            return True
        except Exception as e:
            print(f"Failed to setup driver: {e}")
            return False
    
    def login(self, email, password):
        """
        Attempt to login to Manus AI
        Returns: (success: bool, session_data: dict, error_message: str)
        """
        if not self.setup_driver():
            return False, {}, "Failed to setup browser driver"
        
        try:
            # Navigate to Manus AI login page
            self.driver.get("https://manus.chat/login")
            time.sleep(2)
            
            # Find and fill email field
            email_field = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email'], input[name='email'], input[placeholder*='email' i]"))
            )
            email_field.clear()
            email_field.send_keys(email)
            
            # Find and fill password field
            password_field = self.driver.find_element(By.CSS_SELECTOR, "input[type='password'], input[name='password']")
            password_field.clear()
            password_field.send_keys(password)
            
            # Find and click login button
            login_button = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit'], button:contains('Login'), button:contains('Sign in')")
            login_button.click()
            
            # Wait for login to complete (check for redirect or success indicator)
            time.sleep(5)
            
            # Check if login was successful by looking for dashboard or profile elements
            current_url = self.driver.current_url
            if "login" not in current_url.lower() and "error" not in current_url.lower():
                # Login appears successful, collect session data
                cookies = self.driver.get_cookies()
                session_data = {
                    'cookies': cookies,
                    'url': current_url,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                return True, session_data, "Login successful"
            else:
                # Check for error messages
                try:
                    error_element = self.driver.find_element(By.CSS_SELECTOR, ".error, .alert-danger, [class*='error']")
                    error_message = error_element.text
                except NoSuchElementException:
                    error_message = "Login failed - unknown error"
                
                return False, {}, error_message
                
        except TimeoutException:
            return False, {}, "Login timeout - page elements not found"
        except Exception as e:
            return False, {}, f"Login error: {str(e)}"
        finally:
            if self.driver:
                self.driver.quit()
    
    def verify_session(self, session_data):
        """
        Verify if a stored session is still valid
        Returns: (valid: bool, error_message: str)
        """
        if not session_data or 'cookies' not in session_data:
            return False, "No session data available"
        
        if not self.setup_driver():
            return False, "Failed to setup browser driver"
        
        try:
            # Navigate to Manus AI main page
            self.driver.get("https://manus.chat")
            
            # Add stored cookies
            for cookie in session_data['cookies']:
                try:
                    self.driver.add_cookie(cookie)
                except Exception as e:
                    print(f"Failed to add cookie: {e}")
            
            # Refresh page to apply cookies
            self.driver.refresh()
            time.sleep(3)
            
            # Check if we're logged in by looking for user-specific elements
            current_url = self.driver.current_url
            if "login" not in current_url.lower():
                # Try to find user profile or dashboard elements
                try:
                    # Look for common logged-in indicators
                    user_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                        "[class*='user'], [class*='profile'], [class*='dashboard'], [class*='account']")
                    if user_elements:
                        return True, "Session is valid"
                except:
                    pass
            
            return False, "Session expired or invalid"
            
        except Exception as e:
            return False, f"Session verification error: {str(e)}"
        finally:
            if self.driver:
                self.driver.quit()
    
    def refresh_session(self, email, password, old_session_data=None):
        """
        Refresh session by logging in again
        Returns: (success: bool, session_data: dict, error_message: str)
        """
        # First try to verify existing session
        if old_session_data:
            is_valid, _ = self.verify_session(old_session_data)
            if is_valid:
                return True, old_session_data, "Session still valid"
        
        # If session is invalid or doesn't exist, perform fresh login
        return self.login(email, password)

