# Extracto: Conjuntos

Fuente: `Conjuntos.pdf`. Las páginas indicadas son páginas del PDF (la fuente
didáctica también imprime las páginas 163--207 del libro original).

## Definiciones y principios

- **Conjunto y descripción por propiedad (p. 1):** un conjunto se puede
  describir enumerando elementos o mediante una propiedad que los caracteriza.
- **Subconjunto (p. 1):** `A ⊆ B` significa que todo elemento de `A` también
  pertenece a `B`; la inclusión propia exige además que no sean iguales.
- **Conjunto potencia (p. 2):** `P(S)` es el conjunto cuyos elementos son todos
  los subconjuntos de `S`.
- **Operación binaria (p. 2):** una operación sobre `S` asigna a cada par
  ordenado de elementos de `S` un único resultado que sigue perteneciendo a
  `S`.
- **Unión, intersección, complemento y diferencia (p. 2):** se definen,
  respectivamente, por pertenecer a al menos uno, a ambos, al universo pero no
  al conjunto, y al primer conjunto pero no al segundo.
- **Producto cartesiano (p. 3):** `A × B` contiene los pares ordenados cuyo
  primer componente está en `A` y cuyo segundo componente está en `B`.
- **Principio de multiplicación (p. 7):** una secuencia de elecciones con
  `n1, n2, ...` posibilidades tiene el producto de esas cantidades.
- **Principio de adición (p. 7):** eventos disyuntos con `n1` y `n2`
  resultados tienen `n1 + n2` resultados combinados.
- **Inclusión-exclusión (p. 10):** la cardinalidad de una unión se obtiene
  sumando cardinalidades individuales y alternando sustracciones y sumas de
  intersecciones para no contar dos veces.
- **Principio de clasificación o palomar (p. 11):** al distribuir más de `k`
  objetos en `k` depósitos, algún depósito recibe más de un objeto.

## Teoremas o resultados explícitos

- Si `S` tiene `n` elementos, su conjunto potencia tiene `2^n` elementos
  (p. 2, presentado como práctica).
- El conjunto de los naturales es denumerable (p. 3).
- Si `A` y `B` son finitos y disyuntos, `|A ∪ B| = |A| + |B|` (p. 7).
- Fórmula de inclusión-exclusión para dos y tres conjuntos (p. 10).

## Ejemplos resueltos

- **Ejemplo 2 (p. 1):** al evaluar una definición existencial con cubos se
  obtiene `A = {0, 1, 8}`; otra condición produce todos los naturales y una
  condición universal produce `{0}`.
- **Ejemplo 3 (p. 1):** para `A={1,7,9,15}`, `B={7,9}` y
  `C={7,9,15,20}` se verifican inclusiones, pertenencias y el hecho de que el
  vacío es subconjunto de todo conjunto.
- **Ejemplo 6 (p. 2):** `P({0,1}) = {∅,{0},{1},{0,1}}`.
- **Ejemplo 7 (p. 2):** suma, resta y multiplicación son operaciones binarias
  sobre los enteros porque el resultado sigue siendo un entero único.
- **Ejemplo 10 (p. 2):** una operación definida por casos en naturales no está
  bien definida cuando el mismo par cae en dos casos y recibe dos resultados.
- **Ejemplo 21 (p. 3):** se enumera `0,1,2,...` para justificar que `N` es
  denumerable.
- **Ejemplos 25 y 26 (p. 7):** cuatro dígitos permiten `10^4 = 10000`
  cadenas; sin repetición, `10·9·8·7 = 5040`.
- **Ejemplo 27 (p. 7):** se plantea la selección de tres oficinistas con y sin
  repetición para ilustrar combinaciones y elecciones sucesivas.
- **Ejemplo 30 (p. 7):** 23 autos o 14 camionetas dan 37 opciones por adición.
- **Ejemplos 34 y 35 (p. 8):** números de cuatro dígitos que empiezan en 4 o
  5: `1000+1000 = 2000`, equivalentemente `2·10·10·10`.
- **Ejemplo 37 (p. 8):** números telefónicos con repetición: `10000-5040 =
  4960`.
- **Ejemplo 40 (p. 10):** de 35 votantes, 14 para un referendo y 26 para otro,
  ambos grupos se intersectan en `14+26-35 = 5`.
- **Ejemplo 42 (pp. 10--11):** con datos de compras de brócoli, zanahoria y
  quimbombo, inclusión-exclusión calcula 17 personas que compraron los dos
  primeros.

Las prácticas y ejercicios que solo aparecen enunciados no se consideran
resultados verificados.

Ejemplo 2 (p. 1): Correcto. El documento confirma que evaluar la condición de los cubos arroja 
𝐴
=
{
0
,
1
,
8
}
A={0,1,8}. También establece que 
𝐵
=
𝑁
B=N (los naturales) y que la condición universal produce 
𝐶
=
{
0
}
C={0}.   
Conjuntos.pdf
+ 1

Ejemplo 3 (p. 1): Correcto. Se verifican inclusiones y pertenencias, y explícitamente señala que 
∅
⊆
𝐶
∅⊆C porque el vacío es subconjunto.   
Conjuntos.pdf

Ejemplo 6 (p. 2): Correcto en concepto. El documento ilustra el conjunto potencia con los 4 elementos correspondientes. (Nota: el texto fuente tiene un leve error tipográfico de OCR y escribe 0 en vez de ∅ al inicio de su conjunto de respuesta, pero tu deducción ∅ es la matemáticamente correcta).   
Conjuntos.pdf
+ 1

Ejemplo 7 (p. 2): Correcto. Indica que suma, resta y multiplicación sobre enteros siempre dan un entero único.   
Conjuntos.pdf

Ejemplo 10 (p. 2): Correcto. Demuestra que al evaluar 
5
∘
1
5∘1 en la operación definida por casos, se obtienen dos valores (1 y 0), concluyendo que no está bien definida.   
Conjuntos.pdf

Ejemplo 21 (p. 3): Correcto. Justifica la denumerabilidad de 
𝑁
N listando la secuencia 0, 1, 2, 3, ....   
Conjuntos.pdf

Ejemplos 25 y 26 (p. 7): Correcto. Verifica exactamente tus cálculos: 
10
×
10
×
10
×
10
=
10000
10×10×10×10=10000 (con repetición) y 
10
×
9
×
8
×
7
=
5040
10×9×8×7=5040 (sin repetición).   
Conjuntos.pdf

Ejemplo 27 (p. 7): Correcto. Plantea seleccionar 3 oficinistas de 25, con y sin la posibilidad de atender más de una oficina.   
Conjuntos.pdf

Ejemplo 30 (p. 7): Correcto. Ilustra el principio de adición sumando 23 autos y 14 camionetas para obtener 37 resultados.   
Conjuntos.pdf

Ejemplos 34 y 35 (p. 8): Correcto. Muestra ambas estrategias (adición y multiplicación) para obtener 2000 opciones.   
Conjuntos.pdf

Ejemplo 37 (p. 8): Correcto. Aplica la diferencia 
10000
−
5040
=
4960
10000−5040=4960 para hallar los números telefónicos con repetición.   
Conjuntos.pdf

Ejemplo 40 (p. 10): Correcto. Aplica la fórmula de inclusión-exclusión para hallar la intersección: 
14
+
26
−
35
=
5
14+26−35=5.   
Conjuntos.pdf

Ejemplo 42 (pp. 10-11): Inexacto en un detalle de lectura. El cálculo que da 17 personas es correcto, pero corresponde a quienes compraron brócolis y quimbombos (el primero y el tercer producto mencionado). Quienes compraron los dos primeros (brócolis y zanahorias) fueron un dato dado directamente en el problema: 64 personas.