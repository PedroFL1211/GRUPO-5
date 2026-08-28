import multiplica
import divide
import soma
import subtrai


num1 = float(input("Digite o primeiro número:"))
operador = input("Digite um operador matemático(+,-,*,/):")
num2 = float(input("Digite o segundo número:"))


if operador == '+':
    resultado = soma.somaf(num1,num2)
elif operador == '-':
    resultado = subtrai.subtraif(num1,num2)
elif operador == '*':
    resultado = multiplica.multiplicaf(num1,num2)
elif operador == '/':
    resultado = divide.dividef(num1,num2)

print(resultado)