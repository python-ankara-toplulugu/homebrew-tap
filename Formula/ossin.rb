class Ossin < Formula
  include Language::Python::Virtualenv

  desc "What is OS's sin? 🤔 A beautiful system information utility that displays basic information about your operating system, Python environment, and platform details using Rich for stunning terminal output."
  homepage "https://github.com/python-ankara-toplulugu/ossin"
  # GitHub Sources
  # url "https://github.com/python-ankara-toplulugu/ossin/archive/refs/tags/0.1.1.tar.gz"
  # sha256 "c2e897946f4a95f93f0d86526cb5b2810394afb0ab19e689a93954991bf68a06"
  # PyPI Sourced
  url "https://files.pythonhosted.org/packages/cb/56/69a9a90225047478f4ce12ea3d2f53217a808e14dd3a3cca11e0ddbafd68/ossin-0.1.1.tar.gz"
  # url "https://files.pythonhosted.org/packages/source/o/ossin/ossin-0.1.1.tar.gz"
  sha256 "ad6dbf0389ca8472d099d23245202715c6eb883ed9d200f03897c443f94f2982"
  # version "0.1.1"
  license "MIT"

  depends_on "python@3.14"

  resource "click" do
    url "https://files.pythonhosted.org/packages/3d/fa/656b739db8587d7b5dfa22e22ed02566950fbfbcdc20311993483657a5c0/click-8.3.1.tar.gz"
    sha256 "12ff4785d337a1bb490bb7e9c2b1ee5da3112e94a8622f26a6c77f5d2fc6842a"
  end

  resource "markdown-it-py" do
    url "https://files.pythonhosted.org/packages/5b/f5/4ec618ed16cc4f8fb3b701563655a69816155e79e24a17b651541804721d/markdown_it_py-4.0.0.tar.gz"
    sha256 "cb0a2b4aa34f932c007117b194e945bd74e0ec24133ceb5bac59009cda1cb9f3"
  end

  resource "mdurl" do
    url "https://files.pythonhosted.org/packages/d6/54/cfe61301667036ec958cb99bd3efefba235e65cdeb9c84d24a8293ba1d90/mdurl-0.1.2.tar.gz"
    sha256 "bb413d29f5eea38f31dd4754dd7377d4465116fb207585f97bf925588687c1ba"
  end

  resource "pygments" do
    url "https://files.pythonhosted.org/packages/b0/77/a5b8c569bf593b0140bde72ea885a803b82086995367bf2037de0159d924/pygments-2.19.2.tar.gz"
    sha256 "636cb2477cec7f8952536970bc533bc43743542f70392ae026374600add5b887"
  end

  resource "rich" do
    url "https://files.pythonhosted.org/packages/fb/d2/8920e102050a0de7bfabeb4c4614a49248cf8d5d7a8d01885fbb24dc767a/rich-14.2.0.tar.gz"
    sha256 "73ff50c7c0c1c77c8243079283f4edb376f0f6442433aecb8ce7e6d0b92d1fe4"
  end

  resource "shellingham" do
    url "https://files.pythonhosted.org/packages/58/15/8b3609fd3830ef7b27b655beb4b4e9c62313a4e8da8c676e142cc210d58e/shellingham-1.5.4.tar.gz"
    sha256 "8dbca0739d487e5bd35ab3ca4b36e11c4078f3a234bfce294b0a0291363404de"
  end

  resource "typer" do
    url "https://files.pythonhosted.org/packages/36/bf/8825b5929afd84d0dabd606c67cd57b8388cb3ec385f7ef19c5cc2202069/typer-0.21.1.tar.gz"
    sha256 "ea835607cd752343b6b2b7ce676893e5a0324082268b48f27aa058bdb7d2145d"
  end

  resource "typing-extensions" do
    url "https://files.pythonhosted.org/packages/72/94/1a15dd82efb362ac84269196e94cf00f187f7ed21c242792a923cdb1c61f/typing_extensions-4.15.0.tar.gz"
    sha256 "0cea48d173cc12fa28ecabc3b837ea3cf6f38c6d1136f85cbaaf598984861466"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "ossin", shell_output("#{bin}/ossin --help")
  end
end
