FROM python:3.12-slim

ARG SOURCE_DATE_EPOCH=1785254400
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONHASHSEED=0 \
    TZ=UTC \
    SOURCE_DATE_EPOCH=${SOURCE_DATE_EPOCH} \
    MPLCONFIGDIR=/work/.cache/matplotlib

RUN apt-get update && apt-get install -y --no-install-recommends \
    git make latexmk texlive-bibtex-extra texlive-xetex \
    texlive-latex-extra texlive-fonts-recommended poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /work
COPY . .
RUN python -m pip install --upgrade pip && \
    python -m pip install -r requirements-lock.txt && \
    python -m pip install -e '.[dev]'

CMD ["make", "verify"]
