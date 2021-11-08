from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

wynk_URL = input("Wynk music playlist URL:").strip()
email=input("Prime music email:")
pwd=input("Prime music pwd:")

PATH=r"C:\\Program Files (x86)\\chromedriver.exe"
ser = Service(PATH)
driver = webdriver.Chrome(service=ser)
driver.maximize_window()

def get_wynk_playlist(playlist_URL):
    driver.get(playlist_URL)
    driver.implicitly_wait(10)
    try:
        while True:
            try:
                div = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.ID,"showMoreBtn"))
                    )
                div.find_element(By.TAG_NAME,"a").click()
            except:
                break
        playlist_name = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME,"myPlaylist"))
        )
        playlist_name = playlist_name.find_element(By.TAG_NAME,"h1")
        
        albumList = driver.find_element(By.CLASS_NAME,"albumList")
        all_songs = albumList.find_elements(By.TAG_NAME,"a")
        songs_list=[]
        for i in range(0,len(all_songs),2):
            songs_list.append(all_songs[i].text+" - "+all_songs[i+1].text)
        print("Playlist imported successfully")
    except Exception:
        get_wynk_playlist(playlist_URL)
    
    return {playlist_name.text:songs_list}

def create_prime_music_playlist(imported_playlist,creds):
    login_URL="https://music.amazon.in/my/playlists"
    driver.get(login_URL)
    driver.implicitly_wait(5)
    updated_driver = driver.find_element(By.ID,"accountSetting")
    updated_driver.click()
    
    driver.implicitly_wait(5)
    driver.find_element(By.ID,"signInButton").click()
    driver.implicitly_wait(5)
    
    try:
        email = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID,"ap_email"))
        )
        pwd = driver.find_element(By.ID,"ap_password")
        
        email.send_keys(creds[0])
        pwd.send_keys(creds[1])
        driver.implicitly_wait(5)
        driver.find_element(By.ID,"signInSubmit").click()
        driver.implicitly_wait(10)
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        driver.get(login_URL)
        driver.implicitly_wait(10)

        create_playlist_fld = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME,"_2_399KOSMaMITdNQ_lXtMD"))
        )
        
        create_playlist_fld.find_element(By.TAG_NAME,"music-button").click()

        driver.implicitly_wait(10)
        
        enter_playlist_name = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME,"_3QpxCCZ2ZUyhnlmpwSU7as "))
        )
        enter_playlist_name.clear()
        enter_playlist_name.send_keys(list(imported_playlist.keys())[0])
        driver.implicitly_wait(10)
        driver.find_element(By.ID,"dialogButton1").click()
        print("Playlist created successfully")
    except Exception as e:
        print(e)
        driver.quit()   

def add_music_to_prime(imported_playlist,creds):
    create_prime_music_playlist(imported_playlist,creds)
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[2])
    driver.get("https://music.amazon.in/")
    driver.implicitly_wait(10)
    for song_name in list(imported_playlist.values())[0]:
        try:
            search = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID,"navbarSearchInput"))
            )
            search.clear()
            search.send_keys(99 * Keys.BACKSPACE)
            search.send_keys(song_name)
            driver.find_element(By.ID,"navbarSearchInputButton").click()
            
            driver.implicitly_wait(10)
            
            song_result = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH,"//music-container/music-container/div/music-shoveler[@primary-text='Songs']"))
            )
            
            song = song_result.find_element(By.TAG_NAME,"music-horizontal-item")
            a = song.find_elements(By.TAG_NAME,"music-button")
            songroot = driver.execute_script("return arguments[0].shadowRoot",a[1])
            x=songroot.find_element(By.TAG_NAME,"button")
            driver.implicitly_wait(10)
            action = webdriver.ActionChains(driver)
            action.move_to_element(song)
            action.perform()
            x.click()
            driver.implicitly_wait(5)
            driver.find_element(By.ID,"contextMenuOption1").click()
            driver.implicitly_wait(10)
            recent_playlist = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH,"/html/body/div/music-app/div[2]/div/div/div[4]/div[1]"))
            )
            recent_playlist_list = recent_playlist.find_elements(By.TAG_NAME,"music-image-row")
            
            for el in recent_playlist_list:
                if(el.text == list(imported_playlist.keys())[0]):
                    root = driver.execute_script("return arguments[0].shadowRoot",el.find_element(By.TAG_NAME,"music-button"))
                    driver.implicitly_wait(5)
                    x = root.find_element(By.TAG_NAME,"button")
                    driver.implicitly_wait(5)
                    x.click()
                    driver.implicitly_wait(15)
                    #print(driver.execute_script("return document.body.innerHTML"))
                    if("Duplicate song" in driver.execute_script("return document.body.innerHTML")):
                        print(song_name+" : not added")
                        driver.refresh()                    
                    else:
                        print(song_name+" : added successfully")     
                    break
            
        except Exception:
            print(song_name+" : Couldn't be added")
            try:
                driver.refresh()
            except :
                pass
            

songs_list = get_wynk_playlist(wynk_URL)
add_music_to_prime(songs_list,[email,pwd])
#Add support for more 
