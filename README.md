# codex-dev-workspace

AI 创作与开发工作区。当前包含 **专业 AI 歌曲创作 SOP** 与重庆主题示例单曲资产。

## AI 歌曲创作

- 📘 [AI 歌曲创作 SOP（工具选型 + 五阶段流程）](docs/AI_SONG_CREATION_SOP.md)
- 🎵 示例单曲 [山城夜灯](songs/chongqing-night-lights/)：歌词、Brief、Suno Prompt
- 🛠 本地免费器乐（MusicGen CPU）：

```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install transformers scipy soundfile numpy
python3 scripts/generate_musicgen_segments.py --out output/chongqing_instrumental.wav
```

完整带人声版本：将 `songs/chongqing-night-lights/lyrics.zh.md` 与 `suno-prompt.txt` 粘贴至 [Suno](https://suno.com) Custom 模式（免费层可试听）。

## Git

```bash
git remote add origin https://github.com/<your-user>/codex-dev-workspace.git
git push -u origin main
```
