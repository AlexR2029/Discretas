# Extracto: Funciones

Fuente: `Funciones.pdf`; páginas del PDF.

## Definiciones

- **Función (p. 1):** `f:S→T` es un subconjunto de `S×T` en el que cada
  elemento del dominio aparece exactamente una vez como primer componente.
  `S` es el dominio, `T` el codominio, y `f(s)` la imagen.
- **Rango (p. 1):** conjunto de todas las imágenes de la función.
- **Sobreyectiva (p. 1):** el rango coincide con el codominio.
- **Inyectiva (p. 1):** ningún elemento del codominio es imagen de dos elementos
  distintos del dominio.
- **Biyectiva (p. 2):** función simultáneamente inyectiva y sobreyectiva.
- **Composición (p. 2):** para `f:S→T` y `g:T→U`, `(g∘f)(s)=g(f(s))`.
- **Identidad e inversa (p. 2):** la identidad deja cada elemento fijo; `g` es
  inversa de `f` si `g∘f` y `f∘g` son las identidades correspondientes.
- **Conjuntos equivalentes (p. 2):** dos conjuntos tienen la misma
  cardinalidad cuando existe una biyección entre ellos.

## Ejemplos resueltos

- **Ejemplo 28 (p. 1):** para `f(x,y,z)=xy+z`, se calcula
  `f(-4,3,1)=-63`.
- **Ejemplo 34 (p. 1):** `x↦x^3` de `R` a `R` es sobreyectiva porque toda raíz
  cúbica real tiene preimagen; de `R` a `C` no es sobreyectiva.
- **Ejemplo 35 (p. 1):** `3x+2` de `Q` a `Q` es sobreyectiva usando
  `x=(q-2)/3`; de `Z` a `Q` no lo es.
- **Ejemplo 36 (p. 2):** `x↦x^3` en `R` es inyectiva; `x↦x^2` en `R` no lo
  es; `x↦x^2` en `N` sí lo es.

No se presenta un teorema numerado; las prácticas de composición e inversa y
los ejercicios posteriores son actividades propuestas, no resultados
verificados por la fuente.

Inexacto en la fórmula. En tu resumen escribiste f(x,y,z)=xy+z (multiplicación), pero el documento indica que la función es una exponenciación: 
f(x,y,z)=x^y  +z. El cálculo numérico que presentas sí es correcto, ya que se evalúa como 
𝑓(−4,3,1)=(−4)^3 +1=−64+1=−63

Los otros ejemplos están correctos