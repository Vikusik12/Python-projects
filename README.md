# Python-projects

fileget - The goal of the project is to implement a client for a trivial (read-only) distributed file system.

moje_reseni - vz.dokumentace

interpret - Implementation for interpreting unstructured imperative language IPPcode21.

Skript (interpret.py ) načte XML reprezentaci programu a tento program
s využitím vstupu dle parametrů příkazové řádky interpretuje a generuje výstup.


?xml version="1.0" encoding="UTF-8"?

program language="IPPcode21"
  
  instruction order="1" opcode="CONCAT"
    
    <arg1 type="var">GF@counter</arg1>
    
    <arg2 type="var">GF@counter</arg2>
    
    <arg3 type="string">hi</arg3>
  
  /instruction
 
/program
         
.IPPcode21

DEFVAR GF@counter

MOVE GF@counter string@ #Inicializace proměnné na prázdný řetězec

#Jednoduchá iterace, dokud nebude splněna zadaná podmínka
LABEL while

JUMPIFEQ end GF@counter string@aaa

WRITE string@Proměnná\032GF@counter\032obsahuje\032

WRITE GF@counter

WRITE string@\010

CONCAT GF@counter GF@counter string@a

JUMP while

LABEL end
