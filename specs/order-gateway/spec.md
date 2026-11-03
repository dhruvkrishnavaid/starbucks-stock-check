# Spec: Mobile order gateway and order service

## Brief

The gateway takes a store ID, drinks and add-ins. The order service checks stock and store hours before payment.

## Clarifications

- **Mid-order stock runouts:** stock is reserved before payment. If the reservation fails because stock ran out during the order, the order is refused before payment.

## Acceptance criteria

One criterion per refusal rule in [CLAUDE.md](../../CLAUDE.md). Sample rows are from `data/Starbucks Sample Mobile Orders, Week of 3-9 March 2025.csv`.

| ID | Rule (CLAUDE.md) | Input | Expected refusal |
|---|---|---|---|
| AC-1 | Refuse: store_closed | Order MO-250303-0001 at a closed store, Grande Pike Place Roast, quantity 1, payment not taken | Refused before payment with message: `Bellevue Square is closed right now and can't take mobile orders.` |
| AC-2 | Refuse: base_out_of_stock | Order MO-250304-0007 at SB-10482, Grande Caffè Latte, milk Almondmilk, add-in Vanilla Syrup, quantity 1, Almondmilk has zero stock | Refused before payment, missing component `Almondmilk`, message: `Line 1, Grande Caffè Latte: Almondmilk is unavailable at this store right now.` |
| AC-3 | Refuse: add_in_out_of_stock | Order MO-250305-0014 at SB-10482, Venti Cold Brew, add-in Vanilla Sweet Cream Cold Foam, quantity 1, that add-in has zero stock | Refused before payment, missing component `Vanilla Sweet Cream Cold Foam`, message: `Line 1, Venti Cold Brew: Vanilla Sweet Cream Cold Foam is unavailable at this store right now.` |
| AC-4 | Refuse: insufficient_quantity | Order MO-250307-0028 at SB-11937, Grande Iced Brown Sugar Oatmilk Shaken Espresso, quantity 4, Brown Sugar Syrup stock below the 4 needed | Refused before payment, missing component `Brown Sugar Syrup`, message: `Line 1, Grande Iced Brown Sugar Oatmilk Shaken Espresso: Brown Sugar Syrup is unavailable at this store right now.` |
| AC-5 | Refuse: stock_runs_out_mid_order | Order MO-250307-0024 at SB-10482, Grande Iced Brown Sugar Oatmilk Shaken Espresso, milk Oatmilk, quantity 1, reservation of Oatmilk fails because stock ran out | Refused before payment, missing component `Oatmilk`, message: `Line 1, Grande Iced Brown Sugar Oatmilk Shaken Espresso: Oatmilk is unavailable at this store right now.` |

## Open items

- The sample orders use store IDs with an `SB-` prefix (`SB-10482`, `SB-11937`, `SB-20516`). The stock snapshot uses bare IDs (`10482`, `11307`, `09815`). The mapping between them is not defined, so the sample cannot yet be run against the snapshot.
- Sample order MO-250307-0023 is tagged `stock_runs_out_mid_order` and is accepted. No refusal rule covers it, because it is an accept case. It is not in this spec.
- **Runtime payment loads are an untested risk.** The no-charge check for AC-6 (the payment fake records no calls) only sees calls made through the injected payment client. The suite can prove two things beyond that:
  - A static scan of the order service source fails on any import of a payment SDK outside the adapter module.
  - The same scan fails on `importlib` or `__import__` calls in the order service, because those are the runtime-load paths a source scan can see.

  The suite cannot prove that no runtime load reaches a payment provider in some other form. Closing that needs a network-level check, such as blocking outbound connections to payment hosts in the test environment, which does not exist yet. Until it does, AC-6 does not prove that no payment call happens outside the injected client. Do not read AC-6's no-charge assertion as covering runtime loads.
