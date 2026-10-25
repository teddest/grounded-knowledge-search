FROM node:24.14.1-bookworm-slim

WORKDIR /workspace
ENV NEXT_TELEMETRY_DISABLED=1 \
    WATCHPACK_POLLING=true

RUN npm install --global pnpm@12.14.0

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml .npmrc ./
COPY apps/web/package.json apps/web/package.json
COPY packages/contracts/package.json packages/contracts/package.json
RUN pnpm install --frozen-lockfile

COPY apps/web ./apps/web
COPY packages/contracts ./packages/contracts

EXPOSE 3000
CMD ["pnpm", "--filter", "@grounded/web", "dev"]
