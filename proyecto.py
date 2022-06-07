import ply.lex as lex
import ply.yacc as yacc
import copy
import turtle

# Poner aqui el codigo a ejecutar
data = '''
Program Meep;

var
     int x,a;
     float k;
     char n;

module void func1();
{
     x = 4;
     k = 3.5;
}

module char func2(int y, float l);
var
     int z;
{
     from z = x to y do{
          write("Hello World", z*func3(l));
          l = l+k;
          write("l",l);
     }
     if(l < 10) then{
          return('p');
     }
     return('n');
}

module float func3(float l);
{
     while(l < k) do{
          l = l * 1.25;
     }
     write("k",l);
     k = l;
     return(l);
}

module int func4(int y);
{
     if(y==0 | y==1) then{
          return(y);
     } else {
          return(func4(y-1)+func4(y-2));
     }
}

module void func5();
{
     Color("red");
     Line(200);
     Turn(90);
     Color("blue");
     Point();
     Line(200);
     Turn(90);
     PenUp();
     Line(200);
     Turn(90);
     PenDown();
     Size(10);
     Line(200);
     Turn(90);
}

main()
{
     write( 3+6/3, (3+6)/3 );
     x = 0;
     do{
          write(func4(x));
          x = x+1;
     }while(x<7)
     func1();
     read(a);
     n = func2(func4(a),1);
     write("final",n);
     if(n=='p') then{
          func5();
     }
}

'''

class CalcError(Exception):
    def __init__(self, message):
        self.message = message

reserved = {
    'Program' : 'PROGRAM',
    'main' : 'MAIN',
    'var' : 'VAR',
    'int' : 'INT',
    'float' : 'FLOAT',
    'char' : 'CHAR',
    'void' : 'VOID',
    'module' : 'MODULE',
    'return' : 'RETURN',
    'read' : 'READ',
    'write' : 'WRITE',
    'if' : 'IF',
    'then' : 'THEN',
    'else' : 'ELSE',
    'do' : 'DO',
    'while' : 'WHILE',
    'true' : 'TRUE',
    'false' : 'FALSE',
    'from' : 'FROM',
    'to' : 'TO',
    'Turn' : 'TURN',
    'Line' : 'LINE',
    'Point' : 'POINT',
    'PenUp' : 'PENUP',
    'PenDown' : 'PENDOWN',
    'Color' : 'COLOR',
    'Size' : 'SIZE'
}
 
tokens = ['AND','OR','LE','LT','GE','GT','EQ','NE','EQUAL','LPAREN','RPAREN','LPAREN2','RPAREN2','PUNCOM','COMA','NFLOAT','NINT','SCHAR','SSTRING','SVAR'] + list(reserved.values())

literals = [ '+','-','*','/' ]

t_AND     = r'&'
t_OR      = r'\|'
t_LE      = r'<='
t_LT      = r'<'
t_GE      = r'>='
t_GT      = r'>'
t_EQ      = r'=='
t_NE      = r'!='
t_EQUAL   = r'='
t_LPAREN  = r'\('
t_RPAREN  = r'\)'
t_LPAREN2 = r'\{'
t_RPAREN2 = r'\}'
t_PUNCOM  = r';'
t_COMA    = r','

def t_NFLOAT(t):
    r'\d+\.\d+'
    t.value = float(t.value)    
    return t

def t_NINT(t):
    r'\d+'
    t.value = int(t.value)    
    return t

def t_SCHAR(t):
    r'\'.\''
    return t

def t_SSTRING(t):
    r'\".*\"'
    return t

def t_SVAR(t):
    r'[a-zA-Z][a-zA-Z0-9]*'
    t.type = reserved.get(t.value,'SVAR')    # Check for reserved words
    return t

t_ignore  = ' \t\n'

# Error handling rule
def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(1)

# Build the lexer
lexer = lex.lex()

# Estructura para variables temporales dentro de var
# {
# "nombre_de_funcion ##": {
#    "type": "tipo de variable",
#    "value": "valor de la variable"
#    },
# "contador sys": ##
# }

# Estructura
# {
# "nombre_de_funcion" : {
#    "type": "tipo de funcion"
#    "var": {
#         "nombre_de_variable":{...}
#    },
#    "param": {
#         "nombre_de_parametro":{...}
#    },
#    "run": [(...)]
#    }
# "active sys": "nombre de funcion"
# }
# ejemplo de llamada
# variables["nombre_de_funcion"]["var"]["nombre_de_variable"]["type"]
# inicializado con la funcion main
variables = {"main":{"type":"void","param":{},"run":[],"var":{"contador sys": 0}}}

# Tabla de match
# {
# "tipo1": {
#    "tipo2": {
#         "operando": "tipo de salida"
#         }
#    }
# }
# ejemplo de llamada
# tablaTipos["tipo1"]["tipo2"]["operador"]
tablaTipos = {}

tablaTipos["int"] = {"int": {}, "float": {}, "char": {}, "bool": {}}
tablaTipos["float"] = {"int": {}, "float": {}, "char": {}, "bool": {}}
tablaTipos["char"] = {"int": {}, "float": {}, "char": {}, "bool": {}}
tablaTipos["bool"] = {"int": {}, "float": {}, "char": {}, "bool": {}}

tablaTipos["int"]["int"]["="] = "int"
tablaTipos["int"]["int"]["+"] = "int"
tablaTipos["int"]["int"]["-"] = "int"
tablaTipos["int"]["int"]["*"] = "int"
tablaTipos["int"]["int"]["/"] = "float"
tablaTipos["int"]["int"]["=="] = "bool"
tablaTipos["int"]["int"]["!="] = "bool"
tablaTipos["int"]["int"]["<="] = "bool"
tablaTipos["int"]["int"][">="] = "bool"
tablaTipos["int"]["int"]["<"] = "bool"
tablaTipos["int"]["int"][">"] = "bool"
tablaTipos["int"]["int"]["&"] = "error"
tablaTipos["int"]["int"]["|"] = "error"

tablaTipos["int"]["float"]["="] = "float"
tablaTipos["int"]["float"]["+"] = "float"
tablaTipos["int"]["float"]["-"] = "float"
tablaTipos["int"]["float"]["*"] = "float"
tablaTipos["int"]["float"]["/"] = "float"
tablaTipos["int"]["float"]["=="] = "bool"
tablaTipos["int"]["float"]["!="] = "bool"
tablaTipos["int"]["float"]["<="] = "bool"
tablaTipos["int"]["float"][">="] = "bool"
tablaTipos["int"]["float"]["<"] = "bool"
tablaTipos["int"]["float"][">"] = "bool"
tablaTipos["int"]["float"]["&"] = "error"
tablaTipos["int"]["float"]["|"] = "error"

tablaTipos["int"]["char"]["="] = "error"
tablaTipos["int"]["char"]["+"] = "error"
tablaTipos["int"]["char"]["-"] = "error"
tablaTipos["int"]["char"]["*"] = "error"
tablaTipos["int"]["char"]["/"] = "error"
tablaTipos["int"]["char"]["=="] = "bool"
tablaTipos["int"]["char"]["!="] = "bool"
tablaTipos["int"]["char"]["<="] = "error"
tablaTipos["int"]["char"][">="] = "error"
tablaTipos["int"]["char"]["<"] = "error"
tablaTipos["int"]["char"][">"] = "error"
tablaTipos["int"]["char"]["&"] = "error"
tablaTipos["int"]["char"]["|"] = "error"

tablaTipos["int"]["bool"]["="] = "error"
tablaTipos["int"]["bool"]["+"] = "error"
tablaTipos["int"]["bool"]["-"] = "error"
tablaTipos["int"]["bool"]["*"] = "error"
tablaTipos["int"]["bool"]["/"] = "error"
tablaTipos["int"]["bool"]["=="] = "bool"
tablaTipos["int"]["bool"]["!="] = "bool"
tablaTipos["int"]["bool"]["<="] = "error"
tablaTipos["int"]["bool"][">="] = "error"
tablaTipos["int"]["bool"]["<"] = "error"
tablaTipos["int"]["bool"][">"] = "error"
tablaTipos["int"]["bool"]["&"] = "error"
tablaTipos["int"]["bool"]["|"] = "error"

tablaTipos["float"]["int"]["="] = "float"
tablaTipos["float"]["int"]["+"] = "float"
tablaTipos["float"]["int"]["-"] = "float"
tablaTipos["float"]["int"]["*"] = "float"
tablaTipos["float"]["int"]["/"] = "float"
tablaTipos["float"]["int"]["=="] = "bool"
tablaTipos["float"]["int"]["!="] = "bool"
tablaTipos["float"]["int"]["<="] = "bool"
tablaTipos["float"]["int"][">="] = "bool"
tablaTipos["float"]["int"]["<"] = "bool"
tablaTipos["float"]["int"][">"] = "bool"
tablaTipos["float"]["int"]["&"] = "error"
tablaTipos["float"]["int"]["|"] = "error"

tablaTipos["float"]["float"]["="] = "float"
tablaTipos["float"]["float"]["+"] = "float"
tablaTipos["float"]["float"]["-"] = "float"
tablaTipos["float"]["float"]["*"] = "float"
tablaTipos["float"]["float"]["/"] = "float"
tablaTipos["float"]["float"]["=="] = "bool"
tablaTipos["float"]["float"]["!="] = "bool"
tablaTipos["float"]["float"]["<="] = "bool"
tablaTipos["float"]["float"][">="] = "bool"
tablaTipos["float"]["float"]["<"] = "bool"
tablaTipos["float"]["float"][">"] = "bool"
tablaTipos["float"]["float"]["&"] = "error"
tablaTipos["float"]["float"]["|"] = "error"

tablaTipos["float"]["char"]["="] = "error"
tablaTipos["float"]["char"]["+"] = "error"
tablaTipos["float"]["char"]["-"] = "error"
tablaTipos["float"]["char"]["*"] = "error"
tablaTipos["float"]["char"]["/"] = "error"
tablaTipos["float"]["char"]["=="] = "bool"
tablaTipos["float"]["char"]["!="] = "bool"
tablaTipos["float"]["char"]["<="] = "error"
tablaTipos["float"]["char"][">="] = "error"
tablaTipos["float"]["char"]["<"] = "error"
tablaTipos["float"]["char"][">"] = "error"
tablaTipos["float"]["char"]["&"] = "error"
tablaTipos["float"]["char"]["|"] = "error"

tablaTipos["float"]["bool"]["="] = "error"
tablaTipos["float"]["bool"]["+"] = "error"
tablaTipos["float"]["bool"]["-"] = "error"
tablaTipos["float"]["bool"]["*"] = "error"
tablaTipos["float"]["bool"]["/"] = "error"
tablaTipos["float"]["bool"]["=="] = "bool"
tablaTipos["float"]["bool"]["!="] = "bool"
tablaTipos["float"]["bool"]["<="] = "error"
tablaTipos["float"]["bool"][">="] = "error"
tablaTipos["float"]["bool"]["<"] = "error"
tablaTipos["float"]["bool"][">"] = "error"
tablaTipos["float"]["bool"]["&"] = "error"
tablaTipos["float"]["bool"]["|"] = "error"

tablaTipos["char"]["int"]["="] = "error"
tablaTipos["char"]["int"]["+"] = "error"
tablaTipos["char"]["int"]["-"] = "error"
tablaTipos["char"]["int"]["*"] = "error"
tablaTipos["char"]["int"]["/"] = "error"
tablaTipos["char"]["int"]["=="] = "bool"
tablaTipos["char"]["int"]["!="] = "bool"
tablaTipos["char"]["int"]["<="] = "error"
tablaTipos["char"]["int"][">="] = "error"
tablaTipos["char"]["int"]["<"] = "error"
tablaTipos["char"]["int"][">"] = "error"
tablaTipos["char"]["int"]["&"] = "error"
tablaTipos["char"]["int"]["|"] = "error"

tablaTipos["char"]["float"]["="] = "error"
tablaTipos["char"]["float"]["+"] = "error"
tablaTipos["char"]["float"]["-"] = "error"
tablaTipos["char"]["float"]["*"] = "error"
tablaTipos["char"]["float"]["/"] = "error"
tablaTipos["char"]["float"]["=="] = "bool"
tablaTipos["char"]["float"]["!="] = "bool"
tablaTipos["char"]["float"]["<="] = "error"
tablaTipos["char"]["float"][">="] = "error"
tablaTipos["char"]["float"]["<"] = "error"
tablaTipos["char"]["float"][">"] = "error"
tablaTipos["char"]["float"]["&"] = "error"
tablaTipos["char"]["float"]["|"] = "error"

tablaTipos["char"]["char"]["="] = "char"
tablaTipos["char"]["char"]["+"] = "error"
tablaTipos["char"]["char"]["-"] = "error"
tablaTipos["char"]["char"]["*"] = "error"
tablaTipos["char"]["char"]["/"] = "error"
tablaTipos["char"]["char"]["=="] = "bool"
tablaTipos["char"]["char"]["!="] = "bool"
tablaTipos["char"]["char"]["<="] = "error"
tablaTipos["char"]["char"][">="] = "error"
tablaTipos["char"]["char"]["<"] = "error"
tablaTipos["char"]["char"][">"] = "error"
tablaTipos["char"]["char"]["&"] = "error"
tablaTipos["char"]["char"]["|"] = "error"

tablaTipos["char"]["bool"]["="] = "error"
tablaTipos["char"]["bool"]["+"] = "error"
tablaTipos["char"]["bool"]["-"] = "error"
tablaTipos["char"]["bool"]["*"] = "error"
tablaTipos["char"]["bool"]["/"] = "error"
tablaTipos["char"]["bool"]["=="] = "bool"
tablaTipos["char"]["bool"]["!="] = "bool"
tablaTipos["char"]["bool"]["<="] = "error"
tablaTipos["char"]["bool"][">="] = "error"
tablaTipos["char"]["bool"]["<"] = "error"
tablaTipos["char"]["bool"][">"] = "error"
tablaTipos["char"]["bool"]["&"] = "error"
tablaTipos["char"]["bool"]["|"] = "error"

tablaTipos["bool"]["int"]["="] = "error"
tablaTipos["bool"]["int"]["+"] = "error"
tablaTipos["bool"]["int"]["-"] = "error"
tablaTipos["bool"]["int"]["*"] = "error"
tablaTipos["bool"]["int"]["/"] = "error"
tablaTipos["bool"]["int"]["=="] = "bool"
tablaTipos["bool"]["int"]["!="] = "bool"
tablaTipos["bool"]["int"]["<="] = "error"
tablaTipos["bool"]["int"][">="] = "error"
tablaTipos["bool"]["int"]["<"] = "error"
tablaTipos["bool"]["int"][">"] = "error"
tablaTipos["bool"]["int"]["&"] = "error"
tablaTipos["bool"]["int"]["|"] = "error"

tablaTipos["bool"]["float"]["="] = "error"
tablaTipos["bool"]["float"]["+"] = "error"
tablaTipos["bool"]["float"]["-"] = "error"
tablaTipos["bool"]["float"]["*"] = "error"
tablaTipos["bool"]["float"]["/"] = "error"
tablaTipos["bool"]["float"]["=="] = "bool"
tablaTipos["bool"]["float"]["!="] = "bool"
tablaTipos["bool"]["float"]["<="] = "error"
tablaTipos["bool"]["float"][">="] = "error"
tablaTipos["bool"]["float"]["<"] = "error"
tablaTipos["bool"]["float"][">"] = "error"
tablaTipos["bool"]["float"]["&"] = "error"
tablaTipos["bool"]["float"]["|"] = "error"

tablaTipos["bool"]["char"]["="] = "error"
tablaTipos["bool"]["char"]["+"] = "error"
tablaTipos["bool"]["char"]["-"] = "error"
tablaTipos["bool"]["char"]["*"] = "error"
tablaTipos["bool"]["char"]["/"] = "error"
tablaTipos["bool"]["char"]["=="] = "bool"
tablaTipos["bool"]["char"]["!="] = "bool"
tablaTipos["bool"]["char"]["<="] = "error"
tablaTipos["bool"]["char"][">="] = "error"
tablaTipos["bool"]["char"]["<"] = "error"
tablaTipos["bool"]["char"][">"] = "error"
tablaTipos["bool"]["char"]["&"] = "error"
tablaTipos["bool"]["char"]["|"] = "error"

tablaTipos["bool"]["bool"]["="] = "bool"
tablaTipos["bool"]["bool"]["+"] = "error"
tablaTipos["bool"]["bool"]["-"] = "error"
tablaTipos["bool"]["bool"]["*"] = "error"
tablaTipos["bool"]["bool"]["/"] = "error"
tablaTipos["bool"]["bool"]["=="] = "bool"
tablaTipos["bool"]["bool"]["!="] = "bool"
tablaTipos["bool"]["bool"]["<="] = "error"
tablaTipos["bool"]["bool"][">="] = "error"
tablaTipos["bool"]["bool"]["<"] = "error"
tablaTipos["bool"]["bool"][">"] = "error"
tablaTipos["bool"]["bool"]["&"] = "bool"
tablaTipos["bool"]["bool"]["|"] = "bool"

def buscaTipo(tipo):
     if type(tipo) == type(1):
          return "int"
     elif type(tipo) == type(1.0):
          return "float"
     elif tipo[0] == "'":
          return "char"
     elif tipo[0] == '"':
          return "str"
     elif (tipo == "true" or tipo == "false"):
          return "bool"
     elif variables["main"]["var"].get(tipo) != None:
          return variables["main"]["var"][tipo]["type"]
     elif variables["active sys"] != "main":
          if variables[variables["active sys"]]["var"].get(tipo) != None:
               return variables[variables["active sys"]]["var"][tipo]["type"]
          elif variables[variables["active sys"]]["param"].get(tipo) != None:
               return variables[variables["active sys"]]["param"][tipo]["type"]
     print("ERROR: Tipo de variable no encontrada")
     raise CalcError("Variable invalida")

def buscaVariable(temparam,tempvar,var):
     # Busca la variable en entre las variables globales
     if variables["main"]["var"].get(var) != None:
          return variables["main"]["var"][var]
     elif variables["active sys"] != "main":
          # Si la funcion activa no es main, busca entre los parametros y variables locales recibidos
          if tempvar.get(var) != None:
               return tempvar[var]
          elif temparam.get(var) != None:
               return temparam[var]
     print("ERROR: Variable no encontrada")
     raise CalcError("Variable invalida")

# Estructura
# (op, opdo1, opdo2, result)
# (=, var, null, result)
# (callr, func, param, result)
# (callf, func, param, null)
# (call, func, param, null)
# (goto, null, null, pos)
# (gotof, value, null, pos)
# (return, null, null, result)
# (write, null, null, result)
# (read, null, null, result)

def op(op,opdo1,opdo2):
     if op == '*':
          return opdo1 * opdo2
     elif op == '/':
          return opdo1 / opdo2
     elif op == '-':
          return opdo1 - opdo2
     elif op == '+':
          return opdo1 + opdo2
     elif op == '==':
          return opdo1 == opdo2
     elif op == '<':
          return opdo1 < opdo2
     elif op == '>':
          return opdo1 > opdo2
     elif op == '<=':
          return opdo1 <= opdo2
     elif op == '>=':
          return opdo1 >= opdo2
     elif op == '!=':
          return opdo1 != opdo2
     elif op == '&':
          return opdo1 and opdo2
     elif op == '|':
          return opdo1 or opdo2
     else:
          print("ERROR: OP01")
          raise CalcError("Error en sistema")


def call(function,param,var):
     contador = 0
     while contador < len(variables[function]["run"]):
          a = variables[function]["run"][contador][0]
          b = variables[function]["run"][contador][1]
          c = variables[function]["run"][contador][2]
          d = variables[function]["run"][contador][3]
          # print(contador + 1, ":", a, "|", b, "|", c, "|", d)
          if a == "read":
               # Recibe el apuntador a la variable
               vard = buscaVariable(param,var,d)
               vard["value"] = read(vard["type"])
          elif (a == '*' or a == '/' or a == '-' or a == '+' or a == '==' or a == '>' or a == '<' or a == '<=' or a == '>=' or a == '!=' or a == '&' or a == '|'):
               # Recibe el apuntador a la variable
               varb = buscaVariable(param,var,b)
               # Comprueba que la variable se encuentre inicializada
               if varb.get("value") == None:
                    print("ERROR: Variable no inicializada")
                    raise CalcError("Expresion invalida")
               varc = buscaVariable(param,var,c)
               if varc.get("value") == None:
                    print("ERROR: Variable no inicializada")
                    raise CalcError("Expresion invalida")
               vard = buscaVariable(param,var,d)
               # Recibe el resultado de la operacion
               vard["value"] = op(a,varb["value"],varc["value"])
          elif a == '=':
               # Recibe el apuntador a la variable
               varb = buscaVariable(param,var,b)
               # Comprueba que la variable se encuentre inicializada
               if varb.get("value") == None:
                    print("ERROR: Variable no inicializada")
                    raise CalcError("Expresion invalida")
               vard = buscaVariable(param,var,d)
               # Ejecuta la asignacion
               vard["value"] = varb["value"]
          elif a == "callr" or a == "call":
               # Activa la nueva funcion a ejecutar
               variables["active sys"] = b
               # Hace una copia local de los parametros
               tparam = copy.deepcopy(variables[b]["param"])
               tcont = 0
               # Inicializa cada parametro con el valor recibido
               for x in tparam:
                    varc = buscaVariable(param,var,c[tcont])
                    if varc.get("value") == None:
                         print("ERROR: Variable no inicializada")
                         raise CalcError("Expresion invalida")
                    tparam[x]["value"] = varc["value"]
                    tcont = tcont + 1
               if a == "callr":
                    # Ejecuta la funcion con parametros locales, ya inicializados, y envia una copia local de las variables
                    # Guarda el retorno de la funcion en una variable temporal
                    temp = call(b,tparam,copy.deepcopy(variables[b]["var"]))
                    # Activa la funcion anterior
                    variables["active sys"] = function
                    # Si la funcion regresa un valor, lo guarda en la variable asignada
                    if temp == "Sys None":
                         print("ERROR: No llego a un return la funcion")
                         raise CalcError("Estatuto faltante")
                    else:
                         vard = buscaVariable(param,var,d)
                         vard["value"] = temp
               else:
                    # Ejecuta la funcion con parametros locales, ya inicializados, y envia una copia local de las variables
                    call(b,tparam,copy.deepcopy(variables[b]["var"]))
                    # Activa la funcion anterior
                    variables["active sys"] = function
          elif a == "gotof":
               varb = buscaVariable(param,var,b)
               # Si el valor de la variable es falso, actualiza el contador
               if varb["value"] == False:
                    contador = contador + d - 1
          elif a == "goto":
               # Actualiza el contador
               contador = contador + d - 1
          elif a == "return":
               vard = buscaVariable(param,var,d)
               if vard.get("value") == None:
                    print("ERROR: Variable no inicializada")
                    raise CalcError("Expresion invalida")
               # Regresa el valor de la variable
               return vard["value"]
          elif a == "write":
               vard = buscaVariable(param,var,d)
               if vard.get("value") == None:
                    print("ERROR: Variable no inicializada")
                    raise CalcError("Expresion invalida")
               # Imprime el valor de la variable
               print(vard["value"])
          elif a == "callf":
               tempValues = []
               # Crea un listado con los valores de los parametros recibidos
               for value in c:
                    varc = buscaVariable(param,var,value)
                    tempValues.append(varc["value"])
               # Llama a ejecutar la funcion especial
               callf(b,tempValues)
          else:
               print("ERROR: CALL01")
               raise CalcError("Error en sistema")
          contador = contador + 1
     return "Sys None"

# Funciones especiales
# PenUp() => turtle.penup()
# PenDown() => turtle.pendown()
# Point() => turle.dot(10, 0, 0, 0)
# Turn(nomber) => turtle.left(nomber)
# Line(nomber) => turtle.forward(nomber)
# Color(string) => turtle.pencolor(string)
# Size(nomber) => turtle.pensize(nomber)

def openOutput():
     # Comprueba que el output grafico no haya sido abierto ya
     if variables["output active"] == False:
          variables["output active"] = True
          turtle.shape("turtle")

def callf(func,param):
     # Llama a abrir el output grafico
     openOutput()
     if func == "PenUp":
          turtle.penup()
     elif func == "PenDown":
          turtle.pendown()
     elif func == "Point":
          turtle.dot(10,0,0,0)
     elif func == "Turn":
          turtle.left(param[0])
     elif func == "Line":
          turtle.forward(param[0])
     elif func == "Color":
          turtle.pencolor(param[0])
     elif func == "Size":
          turtle.pensize(param[0])
     else:
          print("ERROR: CALLF01")
          raise CalcError("Error en sistema")

def closeOutput():
     # Comprueba que el output grafico haya sido abierto
     if variables["output active"] == True:
          turtle.exitonclick()

def read(tipo):
     if tipo == "int":
          return int(input())
     elif tipo == "float":
          return float(input())
     elif tipo == "char":
          inputTemp = str(input())
          if len(inputTemp) != 1:
               print("ERROR: Longitud de caracter mayor a 1")
               raise CalcError("Input invalido")
          return inputTemp
     print("ERROR: READ01")
     raise CalcError("Error en sistema")

def run():
     # Declara a main como función activa
     variables["active sys"] = "main"
     # Declara False al output grafico
     variables["output active"] = False
     # Comienza la ejecución con un apuntador a las variables y parámetros globales de main
     call("main",variables["main"]["param"],variables["main"]["var"])
     # Manda a llamar a la última instrucción del output grafico
     closeOutput()
     # print("Run!!")


def p_program(p):
     'program : programInicio decvar decfuntemp programMain'
     for funcion in variables:
          if funcion != "active sys":
               # print("*** ", funcion)
               variables["active sys"] = funcion
               # contador = 1
               for a,b,c,d in variables[funcion]["run"]:
                    # print(contador, ":", a, "|", b, "|", c, "|", d)
                    # contador = contador + 1
                    if (a == '+' or a == '-' or a == '*' or a == '/' or a == '==' or a == '!=' or a == '<=' or a == '>=' or a == '<' or a == '>' or a == '&' or a == '|'):
                         tb = buscaTipo(b)
                         tc = buscaTipo(c)
                         if tablaTipos[tb][tc][a] == "error":
                              print("ERROR: Tipos de valores invalidos")
                              raise CalcError("Expresion invalida")
                         variables[variables["active sys"]]["var"][d] = {"type": tablaTipos[tb][tc][a]}
                    elif a == "gotof":
                         if buscaTipo(b) != "bool":
                              print("ERROR: PROGRAM02")
                              raise CalcError("Expresion invalida")
                    elif a == "=":
                         tb = buscaTipo(b)
                         td = buscaTipo(d)
                         if (tablaTipos[tb][td][a] != td):
                              print("ERROR: Tipo de variable invalido en asignacion")
                              raise CalcError("Estatuto invalido")
                    elif a == "return":
                         if variables[variables["active sys"]]["type"] == "void":
                              print("ERROR: Return en funcion void")
                              raise CalcError("Estatuto invalido")
                         elif variables[variables["active sys"]]["type"] != buscaTipo(d):
                              print("ERROR: Tipo de return invalido")
                              raise CalcError("Estatuto invalido")
                    elif a == "callr":
                         if variables.get(b) == None:
                              print("ERROR: Llamada a funcion invalida")
                              raise CalcError("Estatuto invalido")
                         if variables[b]["type"] == "void":
                              print("ERROR: Llamada con return a funcion void")
                              raise CalcError("Estatuto invalido")
                         else:
                              variables[variables["active sys"]]["var"][d] = {"type": variables[b]["type"]}
                         if len(variables[b]["param"]) != len(c):
                              print("ERROR: Cantidad de parametros invalida")
                              raise CalcError("Estatuto invalido")
                         cont = 0
                         for param in variables[b]["param"]:
                              tc = buscaTipo(c[cont])
                              if (variables[b]["param"][param]["type"] != tc and (variables[b]["param"][param]["type"] == "int" and tc != "float")):
                                   print("ERROR: Tipo de parametro esperado invalido en return")
                                   raise CalcError("Estatuto invalido")
                              cont = cont + 1
                    elif a == "call":
                         if variables.get(b) == None:
                              print("ERROR: Llamada a funcion invalida")
                              raise CalcError("Estatuto invalido")
                         if variables[b]["type"] != "void":
                              print("ERROR: Llamada a funcion con return en llamada void")
                              raise CalcError("Estatuto invalido")
                         elif b == "main":
                              print("ERROR: Llamada a main")
                              raise CalcError("Estatuto invalido")
                         if len(variables[b]["param"]) != len(c):
                              print("ERROR: Cantidad de parametros invalida")
                              raise CalcError("Estatuto invalido")
                         cont = 0
                         for param in variables[b]["param"]:
                              tc = buscaTipo(c[cont])
                              if (variables[b]["param"][param]["type"] != tc and (variables[b]["param"][param]["type"] == "int" and tc != "float")):
                                   print("ERROR: Tipo de parametro esperado invalido")
                                   raise CalcError("Estatuto invalido")
                              cont = cont + 1
                    elif a == "read" or a == "write":
                         buscaTipo(d)
                    elif (a != "callf" and a != "goto"):
                         print("ERROR: PROGRAM01")
                         raise CalcError("Error en sistema")
     print("Compile!!")
     run()

def p_decfuntemp(p):
     'decfuntemp : decfunCodigo decfuntemp'
     pass

def p_decfuntemp02(p):
     'decfuntemp : empty'
     pass

def p_programMain(p):
     'programMain : programMainIni LPAREN2 estatutos RPAREN2'
     variables["main"]["run"] = p[3]
     pass

def p_programMainIni(p):
     'programMainIni : MAIN LPAREN RPAREN'
     variables["active sys"] = "main"
     pass

def p_programInicio(p):
     'programInicio : PROGRAM SVAR PUNCOM'
     variables["active sys"] = "main"
     pass

def p_decvar(p):
     '''
     decvar : VAR decvar2
            | empty
     '''
     pass

def p_decvar2(p):
     '''
     decvar2 : tipo SVAR nomvar decvar2
             | empty
     '''
     if p[1] != None:
          temp = [p[2]]
          temp.extend(p[3])
          for x in temp:
               if variables["main"]["var"].get(x) != None:
                    print("ERROR: Nombre de variable repetido, variable global declarada")
                    raise CalcError("Variable repetida")
               if variables["active sys"] != "main":
                    if variables[variables["active sys"]]["param"].get(x) != None:
                         print("ERROR: Nombre de variable repetido, parametro de funcion declarada")
                         raise CalcError("Variable repetida")
                    if variables[variables["active sys"]]["var"].get(x) != None:
                         print("ERROR: Nombre de variable repetido, variable de funcion declarada")
                         raise CalcError("Variable repetida")
               variables[variables["active sys"]]["var"][x] = {"type": p[1]}
     pass

def p_nomvar(p):
     '''
     nomvar : COMA SVAR nomvar
            | PUNCOM
     '''
     if p[1] != ';':
          temp = [p[2]]
          temp.extend(p[3])
          p[0] = temp
     else:
          p[0] = []
     pass

def p_tipo(p):
     '''
     tipo : INT
          | FLOAT
          | CHAR
     '''
     p[0] = p[1]

def p_decfunCodigo(p):
     'decfunCodigo : decfunCodigoIni LPAREN funpara RPAREN PUNCOM decvar LPAREN2 estatutos RPAREN2'
     variables[variables["active sys"]]["run"] = p[8]
     pass
     

def p_decfunCodigoIni(p):
     'decfunCodigoIni : MODULE funtipo SVAR'
     nombre = p[3]
     funtipo = p[2]
     if variables.get(nombre) != None:
          print("ERROR: Nombre de funcion invalido")
          raise CalcError("funcion repetida")
     variables[nombre] = {}
     variables[nombre]["type"] = funtipo
     variables[nombre]["param"] = {}
     variables[nombre]["run"] = []
     variables[nombre]["var"] = {}
     variables[nombre]["var"]["contador sys"] = 0
     variables["active sys"] = nombre
     pass

def p_funtipo(p):
     '''
     funtipo : tipo
             | VOID
     '''
     p[0] = p[1]
     pass

def p_funpara(p):
     '''
     funpara : tipo SVAR funpara2
             | empty
     '''
     if p[1] != None:
          temp = [(p[1], p[2])]
          temp.extend(p[3])
          for tipo, param in temp:
               if variables["main"]["var"].get(param) != None:
                    print("ERROR: Nombre de parametro invalido")
                    raise CalcError("Variable repetida")
               if variables[variables["active sys"]]["param"].get(param) != None:
                    print("ERROR: Nombre de parametro invalido")
                    raise CalcError("Variable repetida")
               variables[variables["active sys"]]["param"][param] = {"type": tipo}
     pass

def p_funpara2(p):
     '''
     funpara2 : COMA tipo SVAR funpara2
              | empty
     '''
     if p[1] != None:
          temp = [(p[2], p[3])]
          temp.extend(p[4])
          p[0] = temp
     else:
          p[0] = []
     pass

def p_estatutos(p):
     '''
     estatutos : asignacion estatutos
               | llamada estatutos
               | lectura estatutos
               | escritura estatutos
               | desicion estatutos
               | repeticion estatutos
               | funespecial estatutos
     '''
     temp = []
     temp.extend(p[1])
     temp.extend(p[2])
     p[0] = temp
     pass

def p_estatutos02(p):
     '''
     estatutos : retorno
               | empty
     '''
     if p[1] != None:
          p[0] = p[1]
     else:
          p[0] = []
     pass

def p_asignacion(p):
     'asignacion : SVAR EQUAL asitipos PUNCOM'
     final = []
     if p[3][1] == "expr":
          if p[3][0][0][0] != None:
               final.extend(p[3][0])
          final.append( ('=', p[3][0][len(p[3][0])-1][3], None, p[1]) )
     else:
          final.append( ('=', p[3][0], None, p[1]) )
     p[0] = final
     pass

def p_asitipos(p):
     'asitipos : expr'
     p[0] = (p[1],"expr")
     pass

def p_asitipos02(p):
     'asitipos : SCHAR'
     variables[variables["active sys"]]["var"]["contador sys"] = variables[variables["active sys"]]["var"]["contador sys"] + 1
     varTemp = variables["active sys"] + " " + str(variables[variables["active sys"]]["var"]["contador sys"])
     variables[variables["active sys"]]["var"][varTemp] = {"type": "char","value": p[1][1]}
     p[0] = (varTemp,"char")
     pass

def p_expr(p):
     'expr : exprCode'
     pila = []
     final = []
     for x in p[1]:
          if ( x == '+' or x == '-' or x == '*' or x == '/'):
               y = pila.pop()
               z = pila.pop()
               variables[variables["active sys"]]["var"]["contador sys"] = variables[variables["active sys"]]["var"]["contador sys"] + 1
               varTemp = variables["active sys"] + " " + str(variables[variables["active sys"]]["var"]["contador sys"])
               temp2 = (x,z,y,varTemp)
               pila.append(varTemp)
               final.append(temp2)
          elif type(x) != type(1):
               if x[0] == "Sys funcion":
                    parametros = []
                    temp2 = []
                    for para,tipo in x[2]:
                         if tipo == "char":
                              parametros.append(para)
                         else:
                              if para[0][0] == None:
                                   parametros.append(para[0][3])
                              else:
                                   parametros.append(para[len(para)-1][3])
                                   temp2.extend(para)
                    variables[variables["active sys"]]["var"]["contador sys"] = variables[variables["active sys"]]["var"]["contador sys"] + 1
                    varTemp = variables["active sys"] + " " + str(variables[variables["active sys"]]["var"]["contador sys"])
                    temp2.append(("callr",x[1],parametros,varTemp))
                    pila.append(varTemp)
                    final.extend(temp2)
               else:
                    pila.append(x)
          else:
               pila.append(x)
     if final == []:
          final = [(None,None,None,p[1][0])]
     p[0] = final
     pass

def p_exprCode(p):
     'exprCode : expr1 exprCodeT'
     temp = p[1]
     temp.extend(p[2])
     p[0] = temp
     pass

def p_exprCode02(p):
     '''
     exprCodeT : '+' expr1 exprCodeT
               | '-' expr1 exprCodeT
     '''
     temp = []
     temp.extend(p[2])
     temp.append(p[1])
     temp.extend(p[3])
     p[0] = temp
     pass

def p_exprCode03(p):
     'exprCodeT : empty'
     p[0] = []
     pass

def p_expr1(p):
     'expr1 : expr2 expr1T'
     temp = p[1]
     temp.extend(p[2])
     p[0] = temp
     pass

def p_expr12(p):
     '''
     expr1T : '*' expr2 expr1T
            | '/' expr2 expr1T
     '''
     temp = []
     temp.extend(p[2])
     temp.append(p[1])
     temp.extend(p[3])
     p[0] = temp
     pass

def p_expr13(p):
     'expr1T : empty'
     p[0] = []
     pass

def p_expr2(p):
     '''
     expr2 : LPAREN exprCode RPAREN
           | term
     '''
     if p[1] != '(':
          p[0] = [p[1]]
     else:
          p[0] = p[2]
     pass

def p_term(p):
     '''
     term : NINT
          | NFLOAT
     '''
     variables[variables["active sys"]]["var"]["contador sys"] = variables[variables["active sys"]]["var"]["contador sys"] + 1
     varTemp = variables["active sys"] + " " + str(variables[variables["active sys"]]["var"]["contador sys"])
     variables[variables["active sys"]]["var"][varTemp] = {"type": buscaTipo(p[1]),"value": p[1]}
     p[0] = varTemp
     pass

def p_term01(p):
     'term : SVAR posfun'
     if p[2] == None:
          p[0] = p[1]
     else:
          p[0] = ("Sys funcion",p[1], p[2])
     pass

def p_posfun(p):
     '''
     posfun : LPAREN parametros RPAREN
            | empty
     '''
     if p[1] != None:
          p[0] = p[2]
     pass

def p_parametros(p):
     '''
     parametros : asitipos parametros2
                | empty
     '''
     if p[1] != None:
          temp = [p[1]]
          temp.extend(p[2])
          p[0] = temp
     else:
          p[0] = []
     pass

def p_parametros2(p):
     '''
     parametros2 : COMA asitipos parametros2
                 | empty
     '''
     if p[1] != None:
          temp = [p[2]]
          temp.extend(p[3])
          p[0] = temp
     else:
          p[0] = []
     pass

def p_llamada(p):
     'llamada : SVAR LPAREN parametros RPAREN PUNCOM'
     parametros = []
     final = []
     for x in p[3]:
          if x[1] == "char":
               parametros.append(x[0])
          else:
               if x[0][0][0] == None:
                    parametros.append(x[0][0][3])
               else:
                    parametros.append(x[0][len(x[0])-1][3])
                    final.extend(x[0])
     final.append(("call",p[1],parametros,None))
     p[0] = final
     pass

def p_retorno(p):
     'retorno : RETURN LPAREN asitipos RPAREN PUNCOM'
     final = []
     if p[3][1] == "expr":
          if p[3][0][0][0] == None:
               final.append(("return", None, None, p[3][0][0][3]))
          else:
               final.extend(p[3][0])
               final.append(("return", None, None, p[3][0][len(p[3][0])-1][3]))
     else:
          final.append(("return",None,None,p[3][0]))
     p[0] = final
     pass

def p_lectura(p):
     'lectura : READ LPAREN SVAR lectura2 RPAREN PUNCOM'
     temp = [("read", None, None, p[3])]
     for x in p[4]:
          temp.append(("read", None, None, x))
     p[0] = temp
     pass

def p_lectura2(p):
     '''
     lectura2 : COMA SVAR lectura2
              | empty
     '''
     if p[1] != None:
          temp = [p[2]]
          temp.extend(p[3])
          p[0] = temp
     else:
          p[0] = []
     pass

def p_escritura(p):
     'escritura : WRITE LPAREN escritura2 escritura3 RPAREN PUNCOM'
     temp = p[3]
     temp.extend(p[4])
     final = []
     for x in temp:
          if x[1] == "char":
               final.append(("write", None, None, x[0]))
          else:
               if x[0][0][0] == None:
                    final.append(("write", None, None, x[0][0][3]))
               else:
                    final.extend(x[0])
                    final.append(("write", None, None, x[0][len(x[0])-1][3]))
     p[0] = final
     pass

def p_escritura2(p):
     'escritura2 : SSTRING'
     variables[variables["active sys"]]["var"]["contador sys"] = variables[variables["active sys"]]["var"]["contador sys"] + 1
     varTemp = variables["active sys"] + " " + str(variables[variables["active sys"]]["var"]["contador sys"])
     variables[variables["active sys"]]["var"][varTemp] = {"type": "string","value": p[1].replace('"', '')}
     p[0] = [([(None, None, None, varTemp)], 'expr')]
     pass

def p_escritura22(p):
     'escritura2 : asitipos'
     p[0] = [p[1]]
     pass

def p_escritura3(p):
     '''
     escritura3 : COMA escritura2 escritura3
                | empty
     '''
     if p[1] != None:
          temp = []
          temp.extend(p[2])
          temp.extend(p[3])
          p[0] = temp
     else:
          p[0] = []
     pass

def p_desicion(p):
     'desicion : IF LPAREN expresion RPAREN THEN LPAREN2 estatutos RPAREN2 desicion2'
     temp = []
     temp.extend(p[3])
     if p[9] == None:
          temp.append(("gotof", p[3][len(p[3])-1][3], None, len(p[7])+1))
     else:
          temp.append(("gotof", p[3][len(p[3])-1][3], None, len(p[7])+2))
     temp.extend(p[7])
     if p[9] != None:
          temp.append(("goto", None, None, len(p[9])+1))
          temp.extend(p[9])
     p[0] = temp
     pass

def p_desicion2(p):
     '''
     desicion2 : ELSE LPAREN2 estatutos RPAREN2
               | empty
     '''
     if p[1] != None:
          p[0] = p[3]
     pass

def p_repeticion(p):
     '''
     repeticion : condicional
                | nocondicional
     '''
     p[0] = p[1]
     pass

def p_condicional(p):
     'condicional : DO LPAREN2 estatutos RPAREN2 WHILE LPAREN expresion RPAREN'
     temp = []
     temp.extend(p[3])
     temp.extend(p[7])
     temp.append(("gotof", p[7][len(p[7])-1][3], None, 2))
     temp.append(("goto", None, None, -(len(p[3]) + len(p[7]) + 1)))
     p[0] = temp
     pass

def p_condicional02(p):
     'condicional : WHILE LPAREN expresion RPAREN DO LPAREN2 estatutos RPAREN2'
     temp = []
     temp.extend(p[3])
     temp.append(("gotof", p[3][len(p[3])-1][3], None, len(p[3]) + len(p[7]) + 1))
     temp.extend(p[7])
     temp.append(("goto", None, None, -(len(p[3]) + len(p[7]) + 1)))
     p[0] = temp
     pass

def p_expresion(p):
     'expresion : comp1 expresion2'
     temp = []
     temp2 = p[1]
     if p[1][0][0] != None:
          temp.extend(p[1])
     if p[2] != None:
          for x, y in p[2]:
               if y[0][0] != None:
                    temp.extend(y)
               variables[variables["active sys"]]["var"]["contador sys"] = variables[variables["active sys"]]["var"]["contador sys"] + 1
               varTemp = variables["active sys"] + " " + str(variables[variables["active sys"]]["var"]["contador sys"])
               temp.append((x, temp2[len(temp2)-1][3], y[len(y)-1][3], varTemp))
               temp2 = temp
     p[0] = temp
     pass

def p_expresion2(p):
     '''
     expresion2 : comp2 comp1 expresion2
                | empty
     '''
     if p[1] != None:
          temp = [(p[1],p[2])]
          temp.extend(p[3])
          p[0] = temp
     else:
          p[0] = []
     pass

def p_comp2(p):
     '''
     comp2 : AND
           | OR
     '''
     p[0] = p[1]
     pass

def p_comp1(p):
     'comp1 : asitipos comp3 asitipos'
     temp = []
     last1 = ""
     last2 = ""
     if p[1][1] == "expr":
          if p[1][0][0][0] != None:
               temp.extend(p[1][0])
          last1 = p[1][0][len(p[1][0])-1][3]
     else:
          last1 = p[1][0]
     if p[3][1] == "expr":
          if p[3][0][0][0] != None:
               temp.extend(p[3][0])
          last2 = p[3][0][len(p[3][0])-1][3]
     else:
          last2 = p[3][0]
     variables[variables["active sys"]]["var"]["contador sys"] = variables[variables["active sys"]]["var"]["contador sys"] + 1
     varTemp = variables["active sys"] + " " + str(variables[variables["active sys"]]["var"]["contador sys"])
     temp.append((p[2], last1, last2,varTemp))
     p[0] = temp
     pass

def p_comp12(p):
     '''
     comp1 : TRUE
           | FALSE
     '''
     p[0] = [(None, None, None, p[1])]
     pass

def p_comp3(p):
     '''
     comp3 : EQ
           | GT
           | GE
           | LT
           | LE
           | NE
     '''
     p[0] = p[1]
     pass

def p_nocondicional(p):
     'nocondicional : FROM SVAR EQUAL expr TO expr DO LPAREN2 estatutos RPAREN2'
     temp = []
     if p[4][0][0] != None:
          temp.extend(p[4])
     temp.append(("=", p[4][len(p[4])-1][3], None, p[2]))
     if p[6][0][0] != None:
          temp.extend(p[6])
     variables[variables["active sys"]]["var"]["contador sys"] = variables[variables["active sys"]]["var"]["contador sys"] + 1
     varTemp = variables["active sys"] + " " + str(variables[variables["active sys"]]["var"]["contador sys"])
     temp.append(("<=", p[2], p[6][len(p[6])-1][3], varTemp))
     temp.append(("gotof", varTemp, None, len(p[9]) + 4))
     temp.extend(p[9])
     variables[variables["active sys"]]["var"]["contador sys"] = variables[variables["active sys"]]["var"]["contador sys"] + 1
     varTemp = variables["active sys"] + " " + str(variables[variables["active sys"]]["var"]["contador sys"])
     variables[variables["active sys"]]["var"]["contador sys"] = variables[variables["active sys"]]["var"]["contador sys"] + 1
     varTemp2 = variables["active sys"] + " " + str(variables[variables["active sys"]]["var"]["contador sys"])
     variables[variables["active sys"]]["var"][varTemp2] = {"type": "int", "value": 1}
     temp.append(("+", p[2], varTemp2, varTemp))
     temp.append(("=", varTemp, None, p[2]))
     temp.append(("goto", None, None, -(len(p[9]) + len(p[6]) + 3)))
     p[0] = temp
     pass

def p_funespecial(p):
     '''
     funespecial : LINE LPAREN expr RPAREN PUNCOM
                 | TURN LPAREN expr RPAREN PUNCOM
                 | SIZE LPAREN expr RPAREN PUNCOM
     '''
     temp = []
     param = []
     if p[3][0][0] == None:
          param.append(p[3][0][3])
     else:
          temp.extend(p[3])
          param.append(p[3][len(p[3])-1][3])
     temp.append(("callf",p[1],param,None))
     p[0] = temp
     pass

def p_funespecial02(p):
     '''
     funespecial : POINT LPAREN RPAREN PUNCOM
                 | PENUP LPAREN RPAREN PUNCOM
                 | PENDOWN LPAREN RPAREN PUNCOM
     '''
     temp = []
     param = []
     temp.append(("callf",p[1],param,None))
     p[0] = temp
     pass

def p_funespecial03(p):
     'funespecial : COLOR LPAREN SSTRING RPAREN PUNCOM'
     temp = []
     param = []
     variables[variables["active sys"]]["var"]["contador sys"] = variables[variables["active sys"]]["var"]["contador sys"] + 1
     varTemp = variables["active sys"] + " " + str(variables[variables["active sys"]]["var"]["contador sys"])
     variables[variables["active sys"]]["var"][varTemp] = {"type": "string","value": p[3].replace('"', '')}
     param.append(varTemp)
     temp.append(("callf",p[1],param,None))
     p[0] = temp
     pass

def p_empty(p):
     'empty :'
     pass

# Error rule for syntax errors
def p_error(p):
    print("Syntax error in input!")

# Build the parser
yacc.yacc(debug=True)

# Give the lexer some input
lexer.input(data)

# Set up a logging object
import logging
logging.basicConfig(
    level = logging.DEBUG,
    filename = "parselog.txt",
    filemode = "w",
    format = "%(filename)10s:%(lineno)4d:%(message)s"
)
try:
     log = logging.getLogger()
     yacc.parse(data, debug=log)
except CalcError:
    print()
