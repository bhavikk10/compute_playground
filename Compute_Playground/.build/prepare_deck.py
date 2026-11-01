from pathlib import Path
p=Path('.build/finalize.mjs');s=p.read_text().replace('/.build/draft.pptx','/.build/extended-draft.pptx').replace('/docs/presentation.pptx','/docs/presentation-v2.pptx').replace('explicitTotalSlideCount:6','explicitTotalSlideCount:7').replace('presentation.validation.json','presentation-v2.validation.json');p.write_text(s)
