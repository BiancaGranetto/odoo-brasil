import os
import csv
#É utilizado para a conversão da string enviada pelo Odoo (CSV) para uma Matriz
import numpy as np
from docutils.nodes import row
from stdnum.hr import oib

def main(file):
    matrix = []
#Quebra a string, mantendo uma linha original do arquivo CSV por linha na string
    file1 = file.split('\n')

#Loop para criar um array bi-dimensional, que é uma representação que facilita
#as operações que precisarão ser realizadas.
    for i in file1:
        values = i.split(',')
        matrix.append(values)
    matrix = np.array(matrix)
    
#Instânciação das variaveis que serão utilizadas
    dates = []
    balance = []
    ofx_file = ""
    date_start = ""
    date_end = ""
    ofx = ""
#Loop através da Matriz para realizar as operações necessárias
    for i in range(1,len(matrix)): 
        row = matrix[i]#Fornece um ponteiro, onde row será a linha atual do loop
        np.array(row)#Converte de lista -> array para facilitar operações
        if row[0] != "":#Garantia que o código abaixo só se aplique á registros
            dates.append(row[0])#Preenche uma lista com todas as datas da matriz
            if row[6] == "Pago":#Para extrair valores dos registros Pagos 
                date = formatdate(row[0])#Obtém data
                order_number = row[1]#Obtém número da ordem de venda
                partner = row[2]#Obtém quem foi o responsável pela compra 
                value = '%.2f' % int(row[4])#Retorna o preço formatado .00
                balance.append(row[4])#Cálcula o valor total das transações Pagas do CSV
                ofx_file += write_file_transaction(str(value), date, \
                partner, order_number)#Escreve os valores da tag ofx de transação

    balance = '%.2f' % sum(map(int, balance))
    date_start = formatdate(min(dates))
    date_end = formatdate(max(dates))

    ofx_file_start = write_file_start(date_start, date_end)
    ofx_file_end = write_file_end(balance)
    #Escreve os valores OFX
    ofx += ofx_file_start
    ofx += ofx_file 
    ofx += ofx_file_end

    return ofx

def formatdate(date):
    return date[6:10] + date[3:5] + date[0:2]
#Este método é o encarregado de escrever as transações na string final
def write_file_transaction(value, date, partner, order_number):
    return """
    <STMTTRN>
    <TRNTYPE>DEBIT
    <DTPOSTED>%s
    <TRNAMT>%s
    <FITID>%s
    <CHECKNUM>%s
    <MEMO>%s %s
    </STMTTRN>
    """ % (date, value, date, date, partner, order_number)
#Método para escrever o inicio do OFX
def write_file_start(date_start, date_end):
    return """
    <OFX>
    <BANKMSGSRSV1>
    <STMTTRNRS>
    <STMTRS>
    <CURDEF>BRL
    <BANKACCTFROM>
    <BANKID>0755
    <ACCTID>1069001
    <ACCTTYPE>CHECKING
    </BANKACCTFROM>
    <BANKTRANLIST>
    <DTSTART>%s
    <DTEND>%s
    """ % (date_start, date_end)

#Método para escrever o fim do OFX
def write_file_end(balance):
    return """
    </BANKTRANLIST>
    <LEDGERBAL>
    <BALAMT>%s
    </LEDGERBAL>
    </STMTRS>
    </STMTTRNRS>
    </BANKMSGSRSV1>
    </OFX>
    """ % (balance)
