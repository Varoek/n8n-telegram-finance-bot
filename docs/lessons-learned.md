# Lessons learned

Notes from building and debugging this project (useful in interviews and for anyone copying the design).

1. **Design for the failure you actually have.** CGNAT and a home server mean outages are normal. A write-ahead queue,
   idempotency keys and an external heartbeat solved it without paying for hosting.
2. **Let the LLM read, let code calculate.** Extraction goes through a strict JSON contract and validation; totals and comparisons
   never touch the model.
3. **Handled errors are silent.** n8n only calls the error workflow for unhandled failures. Every error output needs its own alert path.
4. **Small UI details cause most outages:**
   - a Switch/IF whose value box contained pasted instructions instead of one word
   - an IF default of "Any condition" that matched every old row and re-ran finished work every 15 minutes
   - a Set node assignment with an empty field name, so `model` was never sent to the API
   - inline keyboard buttons without `callback_data`
   - a stale credential ID after deleting and recreating a credential
5. **A node that returns nothing stops the chain.** Data table updates that match no row need "Always Output Data" or the rest of the workflow never runs.
6. **Test with real inputs early.** Pinned test data with a repeated `update_id` correctly triggered duplicate protection, which looked like a bug.
7. **Keep secrets out from day one.** IDs live in one Config node, credentials in n8n, and a sanitizer script is part of the export workflow.
8. **Debug with the data, not guesses.** Exporting a workflow as JSON lets you check every node name, expression and connection in one pass.
