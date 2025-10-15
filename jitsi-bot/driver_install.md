[chrome drivers](https://developer.chrome.com/docs/chromedriver/)

[firefox drivers](https://github.com/mozilla/geckodriver/releases)
wget https://github.com/mozilla/geckodriver/releases/download/v0.36.0/geckodriver-v0.36.0-linux64.tar.gz

selenium also has a way to auto install and update the drivers but its weird. There 
isn't a package in a package manager (cargo or apt) to handle the driver manager that 
I could find: [selenium manager](https://www.selenium.dev/documentation/selenium_manager/)



#tls cert command:
```bash
openssl s_client -connect jitsi.local:443 < /dev/null 2>/dev/null | openssl x509 > jitsi-local.pem
```
do not forget this if as this took me forever to figure out
