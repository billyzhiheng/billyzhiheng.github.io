# 学术团队站 · 风格融合静态 Demo

## 设计说明

| 来源 | 借鉴内容 |
|------|----------|
| [Wikipedia: Manual of Style/Layout](https://en.wikipedia.org/wiki/Wikipedia:Manual_of_Style/Layout#Headings) | 导语、目录、顶栏与右侧「语言」栏式布局感、H2 底边线、附录顺序等 |
| [Wenqi Fan — Workshops](https://wenqifan03.github.io/workshops.html) | 左窄栏分组导航（Research / Professional / Experience / Links）+ 右主栏大标题与列表 |

## 目录结构

```
academic-team-demo/
├── README.md
├── reference/           # 抓取/摘要说明（非完整镜像）
│   ├── crawled-wikipedia-layout.md
│   └── crawled-wenqifan-structure.md
├── css/
│   └── wiki-team.css
├── index.html           # 首页（英文）— **站点默认语言与默认入口**
├── index.zh.html        # 首页（中文）
├── workshops.html       # Workshops 列表示例
├── members.html
├── publications.html
└── …                    # 招生/Openings 内容仅在 index / index.zh 首页
```

## 语言

- **默认语言：英文**（`<html lang="en">`，入口 `index.html`；`hreflang="x-default"` 指向英文首页）。
- 中文首页为 `index.zh.html`。各英文页右侧「中文」可进入中文首页（子页暂无单独中文版时，进入首页为预期行为）。

## 本地预览

用浏览器直接打开 `index.html`（英文首页），中文首页为 `index.zh.html`。亦可启动静态服务器：

```bash
# Python 3
cd academic-team-demo
python -m http.server 8080
```

浏览器访问 `http://localhost:8080` 即可。

## 版本快照

| 标签 | 说明 |
|------|------|
| `demo-snapshot-2025-03-18` | 侧栏分组导航（Zhiheng Zhao / Research / Experience / Professional Activities / Links）、Members / Openings 等子页与当前样式 |

回退到该快照：`git checkout demo-snapshot-2025-03-18`（或查看：`git show demo-snapshot-2025-03-18`）。

## 说明

- 维基与参考个人页版权归原站点所有；本仓库仅为学习与版式演示。
- 可将整文件夹部署到 GitHub Pages、Netlify 等静态托管。
