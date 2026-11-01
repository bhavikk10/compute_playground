from pathlib import Path
p=Path('experiments/run_experiments.py');s=p.read_text();s=s.replace("    print(df.to_string(index=False))","    print(df.to_string(index=False))\n    from experiments.extended_experiments import main as extended_main\n    extended_main()")
p.write_text(s)
