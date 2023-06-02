from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def devbyParse():
    path = 'https://jobs.devby.io/'
    DRIVER_PATH = './chromedriver.exe'

    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1200")

    # options.add_argument("--disable-blink-features=AutomationControlled")
    # options.add_experimental_option("useAutomationExtension", False)
    # options.add_experimental_option("excludeSwitches", ["enable-automation"])

    service = Service(executable_path=DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=options)
    # driver = webdriver.Chrome(options=options, dri)
    # driver = uc.Chrome(version_main = 112)
    # driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    #     'source': '''
    #         delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
    #         delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
    #         delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
    #     '''
    # })

    driver.get(path)

    button = WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.CLASS_NAME, "wishes-popup__button-close")))
    button.click()
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "vacancies-list__body")))

    vacanciesLinks = driver.find_elements(By.CLASS_NAME, 'vacancies-list-item__link_block')
    vacanciesArray = []

    nextVacancy = "Вакансия " + vacanciesLinks[0].text

    for index in range(len(vacanciesLinks)):
        vacanciesLinks[index].click()

        WebDriverWait(driver, 20).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "title"))
        )

        if (index > 0):
            WebDriverWait(driver, 20).until(
                EC.text_to_be_present_in_element((By.CLASS_NAME, "title"), nextVacancy)
            )

        vacancy = {}
        vacancyName = driver.find_element(By.CLASS_NAME, 'title').text
        vacancy['Название'] = vacancyName[vacancyName.find(" ") + 1:]
        vacancy['Ссылка'] = vacanciesLinks[index].get_attribute("href")
        vacancy['Cкилы'] = driver.find_element(By.CLASS_NAME, 'vacancy__tags').text.split('\n')
        vacancy['Описание'] = driver.find_element(By.CLASS_NAME, 'vacancy__text').text
        vacancy['Компания'] = driver.find_element(By.CLASS_NAME, 'vacancy__header__company-name').text
        info = driver.find_element(By.CLASS_NAME, 'vacancy__info').text.split('\n')

        for i in range(len(info)):
            keyAndValue = info[i].split(': ')
            key = keyAndValue[0]
            value = keyAndValue[1]
            vacancy[key] = value

        for i in vacancy:
            if isinstance(vacancy[i], str):
                vacancy[i] = vacancy[i].replace('"', "'")

        if (index != len(vacanciesLinks) - 1):
            nextVacancy = "Вакансия " + vacanciesLinks[index + 1].text

        vacanciesArray.append(vacancy)

        print(str(index + 1) + '/' + str(len(vacanciesLinks)) + '    ' + str(
            round((index + 1) / len(vacanciesLinks), 3) * 100) + ' %')

    driver.quit()

    return vacanciesArray
