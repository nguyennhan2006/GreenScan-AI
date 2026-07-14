# Push to GitHub

```bash
unzip AI-QUANTUM-GREENWASHING-AGENT-v1.zip
cd ai-quantum-greenwashing-agent

git init
git add .
git commit -m "feat: initial evidence-first greenwashing agent baseline"
git branch -M main
git remote add origin <YOUR_GITHUB_REPOSITORY_URL>
git push -u origin main
```

Recommended branch protection:

- require pull requests;
- require CI test job;
- require one domain/reviewer approval for taxonomy or scoring changes;
- prevent force pushes to `main`;
- enable secret scanning and dependency updates.
