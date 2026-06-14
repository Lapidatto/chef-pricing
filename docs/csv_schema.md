# CSV Schema

The workspace contains eight files in `data/`:

| File | Responsibility |
|---|---|
| `ingredients.csv` | Purchased ingredients and base cost |
| `preparations.csv` | In-house preparations and yield |
| `preparation_components.csv` | Ingredients used in preparations |
| `dishes.csv` | Dishes, food cost, prices, and margin |
| `dish_components.csv` | Ingredients and preparations used in dishes |
| `units.csv` | Units and conversion factors |
| `price_history.csv` | Purchase price history |
| `app_settings.csv` | Workspace preferences |

Files use commas, decimal points, and UTF-8 with BOM. IDs must not be changed
manually. Missing columns block calculations; additional columns produce a
warning.
