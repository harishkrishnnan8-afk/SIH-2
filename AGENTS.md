<!-- LOVABLE:BEGIN -->
> [!IMPORTANT]
> This project is connected to [Lovable](https://lovable.dev). Avoid rewriting
> published git history — force pushing, or rebasing/amending/squashing commits
> that are already pushed — as it rewrites history on Lovable's side and the
> user will likely lose their project history.
>
> Commits you push to the connected branch sync back to Lovable and show up in
> the editor, so keep the branch in a working state.
<!-- LOVABLE:END -->

## Architecture rules
- Workspace pages live under the `_workspace` pathless layout (AppShell); `/login` sits outside it. Why: one shared shell.
- UI reads data only via `src/lib/services` (query options per `/api/v1` endpoint); synthetic data is isolated in `src/lib/demo`. Why: swap to backend by flipping `BACKEND_CONNECTED`.
- Never show full APAAR identifiers by default; use `maskApaar`. Why: privacy requirement.
