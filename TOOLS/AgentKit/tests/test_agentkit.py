import json, os, subprocess, sys, tempfile, unittest
from pathlib import Path
SCRIPT=Path(__file__).resolve().parents[1]/"agentkit.py"
def run(*args,input_text=None,timeout=12,env=None):
    return subprocess.run([sys.executable,str(SCRIPT),*args],input=input_text,capture_output=True,text=True,timeout=timeout,env=env)
class AgentKitTests(unittest.TestCase):
    def test_help_version(self):
        self.assertEqual(run("--help").returncode,0); self.assertIn("0.1.0",run("--version").stdout)
    def test_probe_json(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d,"x.py").write_text("print('ok')"); out=Path(d,"r.json")
            r=run("probe","--root",d,"--json",str(out)); self.assertEqual(r.returncode,0,r.stderr)
            data=json.loads(out.read_text()); self.assertEqual(data["root"],str(Path(d).resolve())); self.assertIn(".py",data["format_capabilities"])
    def test_small_listing(self):
        with tempfile.TemporaryDirectory() as d:
            Path(d,"one.txt").write_text("x"); r=run("probe","--root",d,"--list-files")
            self.assertEqual(r.returncode,0); self.assertIn("ページ選択を省略",r.stdout)
    def test_exactly_50_items_still_offers_selector(self):
        with tempfile.TemporaryDirectory() as d:
            for i in range(50): Path(d,f"{i:03}.txt").write_text("x")
            r=run("probe","--root",d,"--list-files",input_text="50\nq\n")
            self.assertEqual(r.returncode,0); self.assertIn("ページサイズ: 50 / 100 / 200 / 500 / MAX",r.stdout)
    def test_large_listing(self):
        with tempfile.TemporaryDirectory() as d:
            for i in range(51): Path(d,f"{i:03}.txt").write_text("x")
            r=run("probe","--root",d,"--list-files",input_text="50\nq\n")
            self.assertEqual(r.returncode,0); self.assertIn("50 / 100 / 200 / 500 / MAX",r.stdout); self.assertIn("候補ファイル数: 51",r.stdout)
    def test_invalid_root(self):
        r=run("probe","--root","/definitely/not/a/real/path"); self.assertEqual(r.returncode,2); self.assertIn("ERROR",r.stderr)
    def test_locate(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d,"x.txt"); f.write_text("a\nb\nc\n")
            self.assertIn("2 | b",run("locate",str(f),"--start","2","--end","2").stdout)
            self.assertEqual(run("locate",str(f),"--start","99").returncode,2)
    def test_ingest_query(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d,"chat.txt"); f.write_text("first\nTIMEOUT found\n")
            r=run("ingest",str(f),"--query","timeout"); self.assertEqual(r.returncode,0); self.assertIn("2: TIMEOUT found",r.stdout)
    def test_note_name_is_sanitized(self):
        with tempfile.TemporaryDirectory() as d:
            env=os.environ.copy(); env["AGENTKIT_NOTES_DIR"]=d
            r=run("note","memo","--name","../../escape",env=env)
            self.assertEqual(r.returncode,0,r.stderr)
            saved=list(Path(d).glob("*.md")); self.assertEqual(len(saved),1)
            self.assertEqual(saved[0].parent,Path(d)); self.assertNotIn("..",saved[0].name)
    def test_fetch_probe_timeout_stops(self):
        with tempfile.TemporaryDirectory() as d:
            fake=Path(d,"git"); fake.write_text(f"#!{sys.executable}\nimport time\ntime.sleep(5)\n"); fake.chmod(0o755)
            env=os.environ.copy(); env["PATH"]=d+os.pathsep+env.get("PATH","")
            r=run("fetch-probe","https://example.invalid/never.git","--timeout","1",timeout=4,env=env)
            self.assertEqual(r.returncode,124,r.stdout+r.stderr); self.assertIn("タイムアウト",r.stdout)
    def test_timer_zero(self):
        r=run("timer","0"); self.assertEqual(r.returncode,0); self.assertIn("終了予定(local)",r.stdout); self.assertIn("終了予定(UTC)",r.stdout)
if __name__=="__main__": unittest.main(verbosity=2)
