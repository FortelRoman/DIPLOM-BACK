from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.edge.options import Options

def setSalary(vacancy):
    start = -1
    end = -1

    if 'Зарплата' in vacancy:
        zp = vacancy['Зарплата']

        if '—' in zp:
            ind = zp.find('—')
            start = zp[1: ind]
            end = zp[ind + 1: len(zp)]

        elif 'от' in zp:
            ind = zp.find('$')
            start = zp[ind + 1: len(zp)]

        elif 'до' in zp:
            ind = zp.find('$')
            end = zp[ind + 1: len(zp)]

    vacancy['Зарплата от'] = start
    vacancy['Зарплата до'] = end


def devbyParse():
    # DRIVER_PATH = './msedgedriver.exe'
    path = 'https://jobs.devby.io/'

    options = Options()
    options.headless = True
    options.add_argument("--window-size=1920,1200")
    # driver = webdriver.Edge(options=options, executable_path=DRIVER_PATH)
    driver = webdriver.Edge(options=options)
    driver.get(path)

    button = WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.CLASS_NAME, "wishes-popup__button-close")))
    button.click()
    WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "vacancies-list__body")))

    vacancies = driver.find_elements(By.CLASS_NAME, 'vacancies-list-item__link_block')
    vacanciesArray = []

    nextVacancy = "Вакансия " + vacancies[0].text

    for index in range(len(vacancies)):
    # for index in range(3):

        vacancies[index].click()

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

        vacancy['Ссылка'] = vacancies[index].get_attribute("href")

        vacancy['Cкилы'] = driver.find_element(By.CLASS_NAME, 'vacancy__tags').text.split('\n')

        vacancy['Описание'] = driver.find_element(By.CLASS_NAME, 'vacancy__text').get_attribute('innerHTML')

        vacancy['Компания'] = driver.find_element(By.CLASS_NAME, 'vacancy__header__company-name').text

        info = driver.find_element(By.CLASS_NAME, 'vacancy__info').text.split('\n')

        for i in range(len(info)):
            keyAndValue = info[i].split(': ')
            key = keyAndValue[0]
            value = keyAndValue[1]
            vacancy[key] = value

        setSalary(vacancy)

        if 'Режим работы' not in vacancy:
            vacancy['Режим работы'] = 'Не указан'

        if 'Размер компании' not in vacancy:
            vacancy['Размер компании'] = -1

        if 'Возможна удалённая работа' not in vacancy:
            vacancy['Возможна удалённая работа'] = 'Не указано'

        if vacancy["Cкилы"][0] == '':
            vacancy["Cкилы"] = ['Не требуются']

        for i in vacancy:
            if isinstance(vacancy[i], str):
                vacancy[i] = vacancy[i].replace('"', "'")

        print(vacancy['Название'])

        if (index != len(vacancies) - 1):
            nextVacancy = "Вакансия " + vacancies[index + 1].text

        vacanciesArray.append(vacancy)

        print(str(index + 1) + '/' + str(len(vacancies)) + '    ' + str(
            round((index + 1) / len(vacancies), 3) * 100) + ' %')

    driver.quit()

    return vacanciesArray
    #     with open('vacancies.json', 'w', encoding = 'utf-8') as f:
    #         json.dump(vacanciesArray, f, ensure_ascii = False, indent = 4)
