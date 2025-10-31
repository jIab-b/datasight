import argparse
import subprocess
import sys
import time
from pathlib import Path
import urllib.request
import os


def run(cmd, cwd=None, env=None):
	return subprocess.run(cmd, cwd=cwd, env=env, check=True)


def popen(cmd, cwd=None, env=None):
	return subprocess.Popen(cmd, cwd=cwd, env=env)


def wait_http(url, timeout=60.0, interval=1.0):
	start = time.time()
	while time.time() - start < timeout:
		try:
			with urllib.request.urlopen(url) as r:
				if 200 <= r.getcode() < 500:
					return True
		except Exception:
			pass
		time.sleep(interval)
	return False


def up(root: Path, build: bool, no_frontend: bool, frontend_port: int, backend_port: int, reload: bool):
	backend = root / "backend"
	frontend = root / "frontend"
	env = os.environ.copy()
	if build:
		run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], cwd=str(backend))
	run([sys.executable, "init_db.py"], cwd=str(backend), env=env)
	run([sys.executable, "scripts/seed_sample.py"], cwd=str(backend), env=env)
	uvicorn_cmd = [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", str(backend_port)]
	if reload:
		uvicorn_cmd.append("--reload")
	api = popen(uvicorn_cmd, cwd=str(backend), env=env)
	ok = wait_http(f"http://localhost:{backend_port}/api/catalog/datasets", timeout=120)
	if not ok:
		print("backend not ready", file=sys.stderr)
	if no_frontend:
		print(f"backend on http://localhost:{backend_port} (Ctrl-C to stop)")
		try:
			return api.wait()
		except KeyboardInterrupt:
			pass
		finally:
			try:
				api.terminate()
			except Exception:
				pass
			try:
				api.wait(timeout=5)
			except Exception:
				try:
					api.kill()
				except Exception:
					pass
		return 0
	if build or not (frontend / "node_modules").exists():
		run(["npm", "install"], cwd=str(frontend))
	fe_env = os.environ.copy()
	fe_env["VITE_API_URL"] = f"http://localhost:{backend_port}"
	web = popen(["npm", "run", "dev", "--", "--port", str(frontend_port)], cwd=str(frontend), env=fe_env)
	print(f"backend: http://localhost:{backend_port}  frontend: http://localhost:{frontend_port} (Ctrl-C to stop)")
	try:
		ret = web.wait()
		return ret
	except KeyboardInterrupt:
		pass
	finally:
		for p in (web, api):
			try:
				p.terminate()
			except Exception:
				pass
			try:
				p.wait(timeout=5)
			except Exception:
				try:
					p.kill()
				except Exception:
					pass
	return 0


def main():
	parser = argparse.ArgumentParser()
	sub = parser.add_subparsers(dest="cmd")
	p_up = sub.add_parser("up")
	p_up.add_argument("--build", action="store_true")
	p_up.add_argument("--no-frontend", action="store_true")
	p_up.add_argument("--frontend-port", type=int, default=5173)
	p_up.add_argument("--backend-port", type=int, default=8000)
	p_up.add_argument("--reload", action="store_true")
	args = parser.parse_args()
	root = Path(__file__).resolve().parent
	if args.cmd in (None, "up"):
		build = getattr(args, "build", False)
		no_frontend = getattr(args, "no_frontend", False)
		frontend_port = getattr(args, "frontend_port", 5173)
		backend_port = getattr(args, "backend_port", 8000)
		reload = getattr(args, "reload", False)
		return sys.exit(up(root, build, no_frontend, frontend_port, backend_port, reload))
	return sys.exit(1)


if __name__ == "__main__":
	main()
