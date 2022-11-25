from django.http import HttpResponse
from django.shortcuts import render
import email.message
from datetime import datetime
from datetime import date
from pandas_datareader import data as web
import pandas as pd
import matplotlib.pyplot as plt
import smtplib
import streamlit as st
import mysql.connector
import time

senha



#fazendo conexão com o banco de dados
conexao=mysql.connector.connect(
            host='localhost',
            user='root',
            passwd='',
            database='cadastro'
            )

x = conexao.cursor()

conexao.commit()


#fazendo o link para pegar fazer o WebScraping
def get_html_content(company):
    import requests
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
    LANGUAGE = "en-US,en;q=0.5"
    session = requests.Session()
    session.headers['User-Agent'] = USER_AGENT
    session.headers['Accept-Language'] = LANGUAGE
    session.headers['Content-Language'] = LANGUAGE
    html_content = session.get(f'https://www.google.com/search?q={company}').text
    return html_content

#função que irá monitorar os preços das ações, programada para fazer isso de meia em meia hora
def alerta():
    while (1):
        emiteAlerta()
        time.sleep(1800)

#fazendo o WebScraping bruto
def home(request):
    invest_data = None
    invest_data = dict()

    #pegando os dados do usuário, através dos inputs, e armazenando no banco de dados
    if 'name' and 'email' and 'company' and 'limit-superior' and 'limit-inferior' in request.GET:
        name = request.GET.get('name')
        emailpessoal = request.GET.get('email')
        company = request.GET.get('company')
        limit_inferior = request.GET.get('limit-inferior')
        limit_superior = request.GET.get('limit-superior')

    #comando para colocar os dados do usuário no banco de dados
        y = f"insert into participante(nome, email, empresa, limite_inferior, limite_superior) values ('{name}','{emailpessoal}', '{company}', '{limit_inferior}', '{limit_superior}')"
        x.execute(y)
        conexao.commit()



#coletando a empresa inserida pelo usuário e pesquisando ela no Google, para pegar as informações necessárias: nome da empresa, valor da ação, variação absoluta e variação relativa
    if 'company' in request.GET:
        company = request.GET.get('company')
        html_content = get_html_content(company)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')


        invest_data['name'] = soup.find('span', attrs={'class': 'aMEhee PZPZlf'}).text
        invest_data['value'] = soup.find('span', attrs={'class': 'IsqQVc NprOob wT3VGc'}).text
        invest_data['variation_absolute'] = soup.find('span', attrs={'jsname': 'qRSVye'}).text
        invest_data['variation_relative'] = soup.find('span', attrs={'jsname': 'rfaVEf'}).text


#coletando o limite inferior estipulado pelo usuário e comparando com o valor da ação,caso o valor da ação esteja menor que o limite inferior, o usuário receberá um email de alerta de compra,já que a ação está com um preço bom.


    if'limit-inferior' in request.GET:
        limit_inferior = request.GET.get('limit-inferior')
        html_content = get_html_content(company)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        valor = soup.find('span', attrs={'class': 'IsqQVc NprOob wT3VGc'}).text
        valor = valor.replace(',', '.')
        valor = float(valor)

        limit_inferior = float(limit_inferior)

        if valor < limit_inferior:
            enviar_email_compra(invest_data['name'], invest_data['value'], emailpessoal)


#coletando o limite superior estipulado pelo usuário e comparando com o valor da ação,caso o valor da ação esteja maior que o limite superior, o usuário receberá um email de alerta de venda,já que a ação está com um preço alto, e que pode ser um bom momento para a venda.


    if 'limit-superior' in request.GET:
        limit_superior = request.GET.get('limit-superior')
        html_content = get_html_content(company)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')
        valor2 = soup.find('span', attrs={'class': 'IsqQVc NprOob wT3VGc'}).text
        valor2 = valor2.replace(',', '.')
        valor2 = float(valor2)

        limit_superior = float(limit_superior)

        if valor2 >= limit_superior:
            enviar_email_venda(invest_data['name'], invest_data['value'], emailpessoal)



    pass
    return render(request, 'core/home.html', {'invest': invest_data})



#função que envia o email de venda!
def enviar_email_venda(empresa, valor, destinatario):
    corpo_email = f"""
    <p>Prezado(a), </p>
    <p>a ação da {empresa} atingiu o valor de R${valor}</p>
    <p>Esse pode ser um bom momento para vender esse ativo!</p>


    """


    msg = email.message.Message()
    msg['Subject'] = "Alerta de venda de ativo"
    msg['From'] = "joaodorea300@gmail.com"
    msg['To'] = destinatario
    password = senha
    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(corpo_email)

    s = smtplib.SMTP('smtp.gmail.com: 587')
    s.starttls()

    s.login(msg['From'], password)
    s.sendmail(msg['From'], [msg['To']], msg.as_string().encode('utf-8'))
    print('Email enviado')


#função que envia o email de compra
def enviar_email_compra(empresa, valor, destinatario):
    corpo_email = f"""
    <p>Prezado(a), </p>
    <p>a ação da {empresa} atingiu o valor mínimo de R${valor}</p>
    <p>Esse pode ser um bom momento para comprar esse ativo!</p>



    """

    msg = email.message.Message()
    msg['Subject'] = "Alerta de compra de ativo"
    msg['From'] = "joaodorea300@gmail.com"
    msg['To'] = destinatario
    password = senha
    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(corpo_email)

    s = smtplib.SMTP('smtp.gmail.com: 587')
    s.starttls()

    s.login(msg['From'], password)
    s.sendmail(msg['From'], [msg['To']], msg.as_string().encode('utf-8'))
    print('Email enviado')


#função responsável por percorrer o banco de dados, conferindo os usuários cadastrados e enviando alertas de compra ou venda de ações
def emiteAlerta():
    z = 'select * from participante'
    x.execute(z)

    resultado = x.fetchall()

    for m in resultado:
        nome = m[1]
        email = m[2]
        empresa = m[3]
        limite_inferior1 = m[4]
        limite_superior1 = m[5]

        html_content = get_html_content(empresa)
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, 'html.parser')

        valor = soup.find('span', attrs={'class': 'IsqQVc NprOob wT3VGc'}).text
        valor = valor.replace(',', '.')
        valor = float(valor)
        print(valor)

        if valor < limite_inferior1:
            enviar_email_compra(empresa, valor, email)

        if valor >= limite_superior1:
            enviar_email_venda(empresa, valor, email)

''' Chamada da função que irá chamar a função de monitorar os preços (emiteAlerta()) das acões de meia em meia hora, para rodar, basta tirar o comentário!
alerta()
'''















