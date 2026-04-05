# 🔗 Reporte de Integridad

```javascript
          if (fm.fuente && !String(fm.fuente).includes("[" + "[")) {
            fm.fuente = "[" + "[" + fm.fuente + "]]";
            count++;
          }
```
