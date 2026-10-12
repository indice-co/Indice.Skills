# Installing the Indice skills

`marketplace.json` in this folder publishes this repository as a plugin marketplace named `indice`. Despite the folder name, Claude Code, GitHub Copilot CLI, and Codex all read the same file.

You make two choices, then follow the section for your tool.

**What to install**

- **Everything:** the `indice-skills` plugin carries every skill.
- **Specific skills:** each skill is also its own plugin, named after the skill (for example `indice-web-api`). The entries in [`marketplace.json`](marketplace.json) list them with a description of each.

Pick one or the other. Installing both loads the same skill twice.

**Where to install it**

- **On your machine:** the skills are available in every project you open with that tool.
- **In one repository:** the repository declares the skills it wants in a committed file, so they load only there and the whole team gets the same set.

Each tool section shows both forms for a machine install. The per-repository examples use `indice-skills`; to declare specific skills there instead, use one line per skill name.

## Before you start

You need read access to this repository and working git credentials. Check with:

```
git ls-remote https://github.com/indice-co/Indice.Skills.git
```

If that fails, run `gh auth login` and try again.

Skills are picked up when a session starts, so open a new session after any change. The agent then loads a skill on its own when your task matches it.

## Claude Code

**On your machine**

Register the marketplace:

```
claude plugin marketplace add indice-co/Indice.Skills
```

Then install everything:

```
claude plugin install indice-skills@indice
```

Or install specific skills, one command per skill:

```
claude plugin install indice-web-api@indice
claude plugin install indice-iam@indice
```

**In one repository**

Run the same commands from that repository with `--scope project`:

```
claude plugin marketplace add indice-co/Indice.Skills --scope project
claude plugin install indice-skills@indice --scope project
```

They write `.claude/settings.json`. Commit it.

**Check, update, remove**

| To                 | Run                                                                                         |
| ------------------ | ------------------------------------------------------------------------------------------- |
| See what is installed | `claude plugin list`                                                                     |
| Browse the skills  | `/plugin` inside a session                                                                  |
| Get the latest     | `claude plugin marketplace update indice`, then `claude plugin update indice-skills@indice` |
| Remove             | `claude plugin uninstall indice-skills@indice`, then `claude plugin marketplace remove indice` |

## GitHub Copilot CLI

**On your machine**

Register the marketplace:

```
copilot plugin marketplace add indice-co/Indice.Skills
```

Then install everything:

```
copilot plugin install indice-skills@indice
```

Or install specific skills, one command per skill:

```
copilot plugin install indice-web-api@indice
copilot plugin install indice-iam@indice
```

**In one repository**

1. Commit `.github/copilot/settings.json` in that repository:

   ```json
   {
     "extraKnownMarketplaces": {
       "indice": {
         "source": { "source": "github", "repo": "indice-co/Indice.Skills" }
       }
     },
     "enabledPlugins": {
       "indice-skills@indice": true
     }
   }
   ```

2. Each developer opens `copilot` once in that repository, in an interactive session, and trusts the folder. Copilot installs the declared plugin on its own, enabled in this repository and disabled everywhere else.

Copilot reads the same two keys from `.claude/settings.json`, so a repository that already has the Claude Code file from the section above does not need step 1.

The install only happens in an interactive session. A non-interactive run (`copilot -p`) uses the plugin once it is installed but does not install it.

**Check, update, remove**

| To                 | Run                                                                                             |
| ------------------ | ----------------------------------------------------------------------------------------------- |
| See what is installed | `copilot plugin list`, or `/skills` inside a session                                         |
| Browse the skills  | `copilot plugin marketplace browse indice`                                                      |
| Get the latest     | `copilot plugin marketplace update`, then `copilot plugin update`                               |
| Remove             | `copilot plugin uninstall indice-skills@indice`, then `copilot plugin marketplace remove indice` |

## Codex

**On your machine**

Register the marketplace:

```
codex plugin marketplace add indice-co/Indice.Skills
```

Then install everything:

```
codex plugin add indice-skills@indice
```

Or install specific skills, one command per skill:

```
codex plugin add indice-web-api@indice
codex plugin add indice-iam@indice
```

**In one repository**

1. Commit `.codex/config.toml` in that repository:

   ```toml
   [marketplaces.indice]
   source_type = "git"
   source = "https://github.com/indice-co/Indice.Skills.git"

   [plugins."indice-skills@indice"]
   enabled = true
   ```

2. Each developer trusts the project in Codex, then runs this once from the repository:

   ```
   codex plugin marketplace upgrade
   ```

**Check, update, remove**

| To                 | Run                                                                                       |
| ------------------ | ----------------------------------------------------------------------------------------- |
| See what is installed, browse the skills | `codex plugin list`                                                 |
| Get the latest     | `codex plugin marketplace upgrade indice`                                                 |
| Remove             | `codex plugin remove indice-skills@indice`, then `codex plugin marketplace remove indice` |
