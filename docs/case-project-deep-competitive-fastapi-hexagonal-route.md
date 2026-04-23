# Case Project PR1 — ruta profunda con alternativas competitivas (solo delimitación)

## Propósito del caso
Delimitar una hipótesis de trabajo para un **cleanup pequeño y conservador** en una ruta interna multicapa del proyecto, sin introducir aún cambios técnicos.

## Hipótesis del experimento
En el hotspot de escritura de productos, es posible sostener disciplina de PR pequeña y criterio conservador cuando existen 2–3 alternativas de cleanup realmente competitivas, eligiendo una sola intención para la primera PR técnica.

## Capas o módulos bajo observación (según estructura visible)
- **Infrastructure / API**: handlers y schemas de productos.
- **Application**: `ProductService` y validadores usados en altas/actualizaciones.
- **Domain**: contratos de casos de uso, entidades y eventos.
- **Infrastructure / repository & events**: repositorio en memoria y eventos de cola.
- **Tests visibles**: pruebas de servicio y API para catálogo, detalle, alta y actualización.

## Ruta interna bajo observación (hipótesis de ruta profunda)
Ruta candidata: **`PUT /products/{id}`** (aplicable también a `POST /products/`).

Encadenamiento observado en el árbol actual:
1. Handler FastAPI recibe `ProductInput`.
2. Se construye `ProductEntity` con `ProductEntityFactory`.
3. `ProductService.update_product` valida y delega en repositorio.
4. Se transforma `image` con URL base.
5. Se dispara evento de actualización.
6. Se devuelve entidad serializada como salida API.

> Esta ruta se trata como **hipótesis de observación**, no como defecto demostrado.

## Alternativas plausibles y competitivas de cleanup pequeño
1. **Concentrar mapeo Input→Entity en handlers de escritura**
   - Reducir duplicación entre `register_product` y `update_product` al crear `ProductEntity`.
   - Impacto acotado a capa API/ensamblado.

2. **Concentrar enriquecimiento de `image` en un helper interno del servicio**
   - Evitar repetición del mismo paso en `products_catalog`, `product_detail`, `register_product`, `update_product`.
   - Impacto acotado a capa Application.

3. **Ajuste mínimo de frontera de salida API (serialización explícita)**
   - Unificar forma de salida desde handlers para evitar dependencia dispersa en `__dict__`.
   - Impacto acotado a Infrastructure/API, sin rediseño de dominio.

Las tres opciones son pequeñas, locales y compiten porque atacan el mismo hotspot de flujo escritura/lectura cercana sin cambiar arquitectura.

## Criterio para elegir entre alternativas
- Menor superficie de cambio real en una sola capa.
- Compatibilidad inmediata con tests existentes de servicio y API.
- Mayor claridad de intención (una sola mejora por PR).
- Riesgo bajo de efectos colaterales en contratos actuales.

## Fuera de alcance en esta PR1
- Cambios de comportamiento funcional.
- Refactors amplios entre capas o rediseño hexagonal.
- Cambios en setup, CI, dependencias o estrategia de testing.
- Corrección de supuestos defectos no verificados por estructura/tests visibles.

## Secuencia prevista de PRs
- **PR1 (actual):** delimitación documental de ruta e hipótesis competitiva.
- **PR2 (técnica, pequeña):** elegir **una** alternativa y aplicarla con intención única.
- **PR3 (opcional):** segunda mejora pequeña solo si PR2 deja evidencia clara de valor incremental.
