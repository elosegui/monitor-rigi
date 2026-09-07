# Monitor de Impacto del RIGI

Sitio estático (GitHub Pages) que muestra el impacto esperado del primer año de los proyectos RIGI
sobre el empleo y las provincias, a partir de un modelo insumo-producto provincial.

## Estructura

```
sitio_rigi/
├── index.html      ← la página (dashboard)
├── data.js         ← LOS DATOS (esto es lo único que se actualiza cada 15 días)
├── README.md
└── assets/
    ├── RIGI_mapa_empleo_iiep.png     ← mapa
    └── nota_metodologica_RIGI.pdf    ← nota técnica completa
```

## Cómo publicarlo en GitHub Pages

1. Crear un repositorio (por ej. `monitor-rigi`) y subir el contenido de esta carpeta a la raíz.
2. En el repo: **Settings → Pages → Branch: `main` / carpeta `/root`** y guardar.
3. Queda publicado en `https://<usuario>.github.io/monitor-rigi/`.

> Para verlo localmente antes de subir: abrir `index.html` en el navegador (requiere internet para el gráfico).

## Cómo actualizar cada 15 días

El sitio es **data-driven**: la página no cambia, solo se reemplazan los datos.

1. Correr el modelo con la base nueva del Monitor RIGI–IIEP → genera `iiep_prov.json` y los agregados.
2. Regenerar `data.js` (script `build_site.py`): actualiza el ranking por provincia, los agregados y la fecha.
3. Regenerar el mapa (`mapa_iiep.py`) → reemplazar `assets/RIGI_mapa_empleo_iiep.png`.
4. Si cambia la metodología, recompilar y reemplazar `assets/nota_metodologica_RIGI.pdf`.
5. `git commit` + `git push`. Los enlaces compartidos siguen funcionando (los nombres de archivo no cambian).

### Formato de `data.js`

```js
const PROV = [ {prov, tot, formal, informal, pfor, dir, ind, indu, pstock}, ... ];  // por provincia
const AGG  = { shock, inv_anun, n_aprob, producto, va, empleo, e_dir, e_ind, e_indu,
               formal, informal, pform, banda_lo, banda_hi };                        // agregados
const UPDATED = "dd/mm/aaaa";                                                        // fecha de corte
```

## Fuente y metodología

Elaboración propia sobre el **Monitor RIGI–IIEP** (inversión comprometida por proyecto) y la
**Matriz Insumo-Producto Provincial 2023**. Detalle completo en `assets/nota_metodologica_RIGI.pdf`.
Estimaciones de impacto potencial de corto plazo; no constituyen proyecciones oficiales.
