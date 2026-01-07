# GitHub Repository Topics

This file lists the repository topics/tags that should be applied to this GitHub repository.

## Topics List

The topics are defined in `topics.txt`, one per line:

- real-estate
- property-analysis
- uk-housing
- price-prediction
- land-registry
- machine-learning
- data-analytics
- geospatial-analysis
- dashboard
- postgresql

## How to Apply Topics

These topics should be added to the repository through the GitHub UI:

1. Go to the repository homepage on GitHub
2. Click on the gear icon (⚙️) next to "About" on the right sidebar
3. Add the topics listed in `topics.txt`
4. Save changes

Alternatively, topics can be added using the GitHub CLI:

```bash
gh repo edit --add-topic real-estate,property-analysis,uk-housing,price-prediction,land-registry,machine-learning,data-analytics,geospatial-analysis,dashboard,postgresql
```

Or using the GitHub API (requires a personal access token with `repo` scope):

```bash
curl -X PUT \
  -H "Authorization: Bearer YOUR_PERSONAL_ACCESS_TOKEN" \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/yachi2605/uk-housing-market-intelligence-pipeline/topics \
  -d '{"names":["real-estate","property-analysis","uk-housing","price-prediction","land-registry","machine-learning","data-analytics","geospatial-analysis","dashboard","postgresql"]}'
```

Note: Replace `YOUR_PERSONAL_ACCESS_TOKEN` with a fine-grained personal access token that has repository access.
