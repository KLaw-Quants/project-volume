---
layout: default
title: 首页
---

<section class="hero">
  <h1>你好，我是 <span class="highlight">你的名字</span> 👋</h1>
  <p class="lead">
    2028 级悉尼大学（University of Sydney）医学博士（MD）候选人。<br>
    这里记录我从备考、申请到正式踏入医学院的心路历程，以及学习、生活与思考。
  </p>
  <div class="hero-links">
    <a class="btn" href="{{ '/blog/' | relative_url }}">阅读博客</a>
    <a class="btn btn-outline" href="{{ '/about/' | relative_url }}">了解更多</a>
  </div>
</section>

<section class="recent-posts">
  <h2>最新文章</h2>
  {% if site.posts.size > 0 %}
    <ul class="post-list">
      {% for post in site.posts limit:3 %}
        <li>
          <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
          <span class="post-date">{{ post.date | date: "%Y-%m-%d" }}</span>
        </li>
      {% endfor %}
    </ul>
    <p><a href="{{ '/blog/' | relative_url }}">查看全部文章 &rarr;</a></p>
  {% else %}
    <p>还没有文章，敬请期待第一篇更新。</p>
  {% endif %}
</section>
