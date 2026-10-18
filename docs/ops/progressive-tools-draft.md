# Progressive procurement tools — package Draft

Source only, 2026-10-18. B2B base: `764b9864`, retaining #397 geometry bindings, modern cache metadata and #396 UI. Corresponding B2B implementation head: `81786f9e`; the full head and Draft PR are linked from this PR. Full operation mapping, preserved gates, validation and host limits are in B2B `docs/design/procurement-progressive-tools-draft.md`.

The skill now teaches `procurement_search → procurement_info → returned entrypoint`; common operations use guarded query/mutate envelopes. RFQs share `rfq.prepare` and `rfq.submit` with explicit session/design/folder sources. Official file upload, minimal identity, native design sidebar and commercial prepare/read/execute remain dedicated. Retired inline approval instructions and the old click-based default prompt were replaced with the current conversation-decision contract. The local root skill and bundled skill/reference/agent files are synchronized; detailed progressive protocol rules have one reference file per skill tree.

The package follows the current B2B compact canonical skill, with the same source for native sidebar/get_design_links and retired-inline boundaries. No plugin identity, App binding, manifest version, OAuth registration, credentials, scopes, network/CSP, installation or saved account plugin was changed. Review/merge/deployment and account plugin updates belong to the parent. Package metadata retains its original identity/version because this is a review Draft, not a release.

Validation:

- `python -m unittest discover -s scripts -p 'test*.py' -v`: 2 PASS.
- Existing `scripts/package_plugin.py` builds a 13-file full Draft and 9-file skills-only App overlay. Archive inspection confirms progressive reference inclusion, no credential/cache files, and no App binding in the skills-only overlay. A packaged file is not deployment or real-host evidence.
- Local and bundled SKILL, agent prompt and workflow/protocol references match byte-for-byte.
- B2B current-main targeted tests are run with dedicated loopback MySQL fixtures; final results: 95 top-level Go PASS, zero FAIL, one separately configured real-producer SKIP; all five formerly skipped MySQL cases and the new facade RFQ MySQL case execute. Native sidebar protocol: 51 Node PASS. Actual Gemini/Claude/Codex refreshing, OAuth challenges, file injection and native App/model acceptance remain unverified for this Draft.

The canonical source is the committed skill tree. Review ZIPs are temporary local outputs under `.tmp/` and are deliberately not committed. No online RFQ, mail, upload or commercial action was performed.

CI follow-up: B2B run 39091103006 exposed the unchanged 8,053-byte core-Skill budget. The failure was locally reproduced at 9,680 bytes. The synchronized core is now 7,859 bytes, with detailed progressive and full website-login rules retained in its on-demand reference. The first instruction explicitly routes procurement_guide through procurement_query; subsequent non-dedicated names are operation IDs. Budgets and mandatory safety facts were not relaxed. Python tests and both package builds pass again.
