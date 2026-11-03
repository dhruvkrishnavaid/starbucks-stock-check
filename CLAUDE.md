# CLAUDE.md

Read this file at the start of every session. The rules below are binding.

## Firm rules

1. **Fixed OpenAPI contracts.** Every endpoint must match its committed OpenAPI contract. Never change a contract to fit an implementation. A contract changes only through its own reviewed change.
2. **No shared database.** Each service must own its data. Never let two services read or write the same database.
3. **Tests before merge.** Contract tests must pass before any change merges. Never merge with failing or skipped contract tests.

## Refusal rules

Each refused `scenario_tag` in the sample orders (`data/Starbucks Sample Mobile Orders, Week of 3-9 March 2025.csv`) has one rule. The order service must check stock and store hours before payment and refuse the order when a rule applies.

Message formats:
- Store closed: `{store_name} is closed right now and can't take mobile orders.`
- Component unavailable: `Line {n}, {size} {drink_name}: {component_name} is unavailable at this store right now.`

### Refuse: store_closed

- The order service must refuse any order at a store that is closed, before payment, with the store-closed message.
- Never accept an order at a closed store.

### Refuse: base_out_of_stock

- The order service must refuse any order whose drink base (for example, a milk) has no stock at the store, before payment, with the component-unavailable message naming that base.
- Never accept an order that uses an out-of-stock base.

### Refuse: add_in_out_of_stock

- The order service must refuse any order whose add-in has no stock at the store, before payment, with the component-unavailable message naming that add-in.
- Never accept an order that uses an out-of-stock add-in.

### Refuse: insufficient_quantity

- The order service must refuse any order whose requested quantity of a component exceeds the stock on hand minus reserved, before payment, with the component-unavailable message naming that component.
- Never accept an order that asks for more of a component than is available.

### Refuse: stock_runs_out_mid_order

- Stock is reserved before payment. The order service must refuse any order whose reservation for a component fails because stock ran out during the order, before payment, with the component-unavailable message naming that component.
- Never take payment for an order whose stock reservation has failed.
