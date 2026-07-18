# SHB LexFold

Máy tính hiệu lực pháp quy ba trục thời gian + tầng trả lời có kiểm chứng.
Toàn bộ spec nằm ở `docs/` (00 vision · 01 decisions · 02 domain · 03 system · 04 corpus/eval · 05 demo).

## Chạy

```bash
docker compose up --build
# API      http://localhost:8000/healthz
# Chat UI  http://localhost:8501
# Admin UI http://localhost:8502
```

Schema Postgres tự áp từ `db/schema.sql` lần khởi tạo đầu (volume `pgdata`).

## Deploy (commit là lên — giám khảo chấm qua URL bất cứ lúc nào)

Mô hình: 1 VPS chạy `docker compose`, GitHub Actions ssh vào pull + rebuild sau mỗi push lên `master`
(`.github/workflows/deploy.yml`). Layer dependency được cache trên server nên rebuild sau commit chỉ mất vài giây.

**Setup một lần trên VPS** (Ubuntu, ≥ 8GB RAM vì BGE-M3 + torch; mở port 8000/8501/8502):

```bash
curl -fsSL https://get.docker.com | sh
ssh-keygen -t ed25519 -f ~/.ssh/deploy -N ''   # key riêng cho CI
cat ~/.ssh/deploy.pub >> ~/.ssh/authorized_keys
git clone git@github.com:ForwardInfinity/lexfold.git ~/lexfold   # hoặc https + PAT
cd ~/lexfold && cp .env.example .env           # điền LLM_API_KEY / JUDGE_API_KEY thật
docker compose up -d --build                   # lần đầu lâu (tải torch), từ đó có cache
```

**Secrets trên GitHub** (Settings → Secrets and variables → Actions): `DEPLOY_HOST` (IP VPS),
`DEPLOY_USER`, `DEPLOY_SSH_KEY` (nội dung private key `~/.ssh/deploy`). Chưa set thì workflow tự skip.

URL cho giám khảo: `http://<IP>:8501` (chat) · `http://<IP>:8502` (admin) · `http://<IP>:8000/healthz`.

Lưu ý vận hành khi đang iterate nhanh:
- `db/schema.sql` chỉ tự áp khi volume `pgdata` còn trống. Đổi schema ⇒ ssh vào VPS chạy
  `make db-reset` rồi ingest lại corpus (dữ liệu là dẫn xuất từ corpus + op, reset không mất gì).
- Deploy chạy song song với CI (không chờ test) — tối ưu vòng lặp; hỏng thì `git revert` + push là rollback.

## Dev local

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e . --group dev
docker compose up -d postgres
export DATABASE_URL=postgresql://lexfold:lexfold@localhost:5432/lexfold
uvicorn api.main:app --reload
```

## Cấu trúc (docs/03 §S8)

| Thư mục | Sở hữu | Spec |
|---|---|---|
| `corpus/` | văn bản gốc + fixtures + `manifest.json` (ground truth đếm tay) | 04 §1 |
| `ingest/` | normalize, parser cây, citation→edge, op extraction, roles | 02, 03 §S4.1–S4.3 |
| `engine/` | fold, windows, scope, snapshot, conflict, sweep, oracle, blast-radius, invariants | 03 §S4.5–S4.8 |
| `retrieval/` | BM25 + dense + RRF, closure, query-builder (một cửa audience) | 03 §S5.2–S5.3 |
| `answer/` | question compiler, composer, verifier 2 tầng, tiers, LLM gateway | 03 §S5 |
| `api/` | FastAPI + Pydantic schemas | 03 §S6 |
| `ui/` | Streamlit chat + admin (admin làm TRƯỚC — R-17) | 03 §S7 |
| `eval/` | golden set, runner, baseline naive RAG, metrics | 04 |
