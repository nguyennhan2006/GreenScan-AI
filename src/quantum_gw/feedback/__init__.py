"""feedback-loop-v1: reviewer decisions make the next version better, never the next click.

The design and its safety rules are in docs/03-architecture/FEEDBACK_LOOP.md.
In one paragraph: a reviewer's decision (storage/reviews.py) is an audit record
and, once finalized, a label. Labels feed five tiers, cheapest and safest first:

0. pointer labels  - the passage that decided the case, so a label says *where*
                     the machine went wrong (reviews.classify_stage);
1. GS-Feedback     - every finalized decision becomes a frozen regression case,
                     and a case once passed may not fail again (bench.py);
2. precedents      - similar claims a person already decided are shown beside a
                     verdict and may raise a claim into the queue (precedents.py);
3. rule miner      - grouped overrides become measured, versioned proposals for
                     the cue lexicon, the rule pack or an org pack (miner.py);
4. trained models  - a stance model trained on clean labels runs in shadow and
                     replaces nothing until it beats the champion on held-out
                     data without more dangerous errors, and a person signs
                     (dataset.py, stance_model.py, registry.py).

Two mechanisms keep the loop clean: active learning picks the items whose label
teaches most (active.py) and label hygiene keeps the checked company's labels,
unresolved disagreements and other organisations' labels out (hygiene.py).

Nothing in this package changes a verdict, a risk score or a release status.
"""
