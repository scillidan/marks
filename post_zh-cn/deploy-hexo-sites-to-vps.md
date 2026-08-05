```
Date: 2015.08.16
Author: 回风
```

# Deploy Hexo sites to VPS

**参考以下内容，感谢原作者，转载留个链接:**

> Berry的博客：(链接已重定向)。  
> 添加新用户，SSH设置，参考了Linode官方帮助：[Securing Your Server](https://web.archive.org/web/20180412094819/https://www.linode.com/docs/security/securing-your-server/)。

两种方法：

1. 在VPS上执行`hexo server`，再配置Nginx反向代理，让blog的域名指向`http://localhost:4000`。
2. 在本地生成静态文件，把静态文件部署到VPS上，用Nginx直接做Web服务。（嗯，我喜欢这种，就用这种吧）

## Nginx配置

在Nginx中新建虚拟主机，我用的是linuxeye的oneinstack包安装的环境，所以，我的新建只需要`sudo ./vhost.sh`即可，然后将blog文件通过sftp或者scp上传到网站目录。

## 自动部署

自动部署的意思是，每当我们执行`hexo d`后，我们的网站信息就发布到服务器上的虚拟目录里。一般的部署方式要么是git要么是rsync，rsync需要本地计算机和服务器都安装了rsync，然后是一翻配置，这里我们用更方便好用的Git来实现：

### Git 安装

> 若无特殊说明，所有安装都在CentOS-7.1上完成

- 想安装git 1.× 版本，在VPS上输入`sudo yum install git`
- 想安装git 2.× 版本，在VPS上输入`sudo yum install git2u`

生成SSH秘钥

如果本机是linux或者Mac OS那就好办了，如果没有生成过ssh秘钥对可输入`ssh-keygen -t rsa -C "blog"`然后一路回车，问密码的地方可以留空，这样这个ssh连接就不在询问密码了，如果你输入了密码，奖励ssh连接的时候是要输入密码的。

然后，我们可以在当前执行用户的目录下找到这个目录（隐藏的）`cd ~/.ssh`，`ls -a`可以看到有id_rsa，id_rsa.pub和known_hosts三个文件，其中id_rsa.pub是公钥。

*注意*：如果你事通过`ssh-keygen -t rsa -C "blog"`命令新建的ssh密钥对，那么秘钥对的名字应该是blog，blog.pub。

多说两句，老鸟请绕行，公钥就是给别人的，放别人那里，私钥可以理解为是你这台机器的指纹，所以服务器上的当前用户目录下的`~/.ssh/authorized_keys`文件里应当包含你的公钥，这样你SSH的时候，服务器明白，“哦，我有你的公钥，你的私钥和公钥配对，证明了你是自己人，可以进入系统”。

*注意*：`authorized_keys`文件不一定是存在的，新建的服务器用户下面是没有这个文件的，需要自己`touch`进去，如果已经有这个文件了，里面应该有很多行，每行代表一个可以ssh连接的主机的公钥。

### 服务器端配置

新建用户git：

`sudo adduser git`

切换至git用户:`su git`，然后初始化git用户的环境

```bash
cd ~
mkdir .ssh && cd .SSH
touch authorized_keys
vim authorized_keys
```

把blog.pub（刚才新建的）或id_rsa.pub的内容粘贴到authorized_keys

在终端输入`ssh git@your-ip-or-domain`，如果能远程登录说明没有问题了。如果出问题了，请试试看看运行 `ll -a /home/git/`，看看`.ssh`目录的拥有者是否是`git:git`，实在不行就运行：

```bash
chown -R git:git .ssh
chmod 700.ssh
chmod 600 .ssh/authorized_keys
```

为静态内容新建仓库：

```bash
cd ~
mkdir blog.git && cd blog.git
git init --bare
```

### 本地设置

设置git用户名

```bash
git config --global user.email "email@example.com"
git config --global user.name "username"
```

修改hexo配置文件里的deploy选项，`git@12.34.56.78:`后面跟的`yournick/abcd.git`相当于服务器目录:`/home/git/yournick/abcd.git/`

```bash
deploy:
type: git
repo: git@12.34.56.78:younick/abcd.git，master
```

运行`hexo g``hexo d`，如果一切正常，静态文件已经被成功的push到了blog的仓库里，如果出现`appears not to be a git repo`的错误，删除hexo目录下的.deploy后再次`hexo g``hexo d`就可以了

### Git hooks

如果你上面都执行成功了，会发现，服务器的`/home/git/….git/branches/`目录是空的。这里引用下Berry在他的文章中的解释：

> 既然`blog.git`是一个仓库，那么只要`git clone /home/git/blog.git`就可以取出仓库的内容了。顺着这个思路就有了下面的想法，使用git hooks在每次push完成后，执行一段脚本，把`blog.git`里的内容`clone`出来，再复制到`/var/www/blog`目录。

在`/home/git/….git/branches/`目录下会由`hooks`目录，里面可以写脚本，Berry的意思就是，每次`hexo d`提交了以后，网站数据进入git的之后执行脚本，将刚入进来的数据拷贝到网站目录去。

```bash
cd ~/blog.git/hooks
touch post-receive
vi post-receive
```

使用下面的脚本

```bash
#!/bin/bash -l
GIT_REPO=/home/git/blog.git
TMP_GIT_CLONE=/tmp/blog
PUBLIC_WWW=/var/www/blog
rm -rf ${TMP_GIT_CLONE}
git clone $GIT_REPO$TMP_GIT_CLONE
rm -rf ${PUBLIC_WWW}/*
cp -rf ${TMP_GIT_CLONE}/* ${PUBLIC_WWW}
```

*注意*：脚本里的`rm`等命令是否能执行成功有git的权限和它所操控的目录决定，所以我们要根据需要的修改下权限

赋予脚本的执行权限：`chmod +x post-receive`

赋予git对网站目录的所有权：`chown git:git -R 你的网站目录位置`

以上执行完后，虽然我们这次部署的是静态网站，但是如果是php等动态网站的话，会发现，静态页面可以解析，动态页面解析不了，所以这里建议：

修改php-fpm（如果你是用它来解析php）的配置文件`www.conf`，让`user = git`下面这项是我自己的个人爱好，你可以不做:

让git的权利再大点，比如，修改nginx的`nginx.conf`文件，让`user`为`git git`，使它成为nginx的操作用户。

---

完工！！