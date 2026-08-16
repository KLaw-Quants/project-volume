# 个人网站 · 博客

一个基于 [Jekyll](https://jekyllrb.com/) 的个人主页 + 博客，通过 GitHub Pages 免费部署。

> 本仓库同时保留了原有的量化研究相关目录（`backtests/`、`data/`、`notebooks/`、`scripts/`、`reports/`），网站构建时已在 `_config.yml` 的 `exclude` 中排除，互不影响。

## 目录结构

```
_config.yml       站点配置
_layouts/         页面模板（default / post）
_includes/        头部 / 底部等公共片段
_posts/           博客文章（Markdown，按 YYYY-MM-DD-标题.md 命名）
assets/css/       样式
index.md          首页
about/            关于我
blog/             博客列表页
contact/          联系方式
```

## 写新文章

在 `_posts/` 下新建文件，命名格式为 `年-月-日-标题.md`，例如：

```
_posts/2026-09-01-my-second-post.md
```

文件开头写 front matter，然后正文用 Markdown：

```markdown
---
title: "文章标题"
date: 2026-09-01
tags: [标签1, 标签2]
---

正文内容……
```

Push 到 `main` 分支后会自动构建部署。

## 本地预览（可选，需要 Ruby）

```bash
bundle install
bundle exec jekyll serve
# 浏览器打开 http://localhost:4000
```

## 部署到 GitHub Pages

本仓库已包含 `.github/workflows/pages.yml`，push 到 `main` 分支会自动构建并部署。

**首次使用需要手动开启一次**：进入仓库 `Settings → Pages`，将 `Source` 改为 **GitHub Actions**（只需设置一次）。之后每次 push 都会自动发布。

## 修改个人信息

以下文件里有占位内容，替换成你自己的信息即可：

- `_config.yml`：站点标题、作者、邮箱
- `index.md`：首页文案
- `about/index.md`：个人介绍、求学经历
- `contact/index.md`：邮箱、社交链接
