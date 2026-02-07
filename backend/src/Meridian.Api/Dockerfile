FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base
WORKDIR /app
EXPOSE 8080

FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY ["src/Meridian.Api/Meridian.Api.csproj", "src/Meridian.Api/"]
COPY ["src/Meridian.Core/Meridian.Core.csproj", "src/Meridian.Core/"]
COPY ["src/Meridian.Infrastructure/Meridian.Infrastructure.csproj", "src/Meridian.Infrastructure/"]
COPY ["src/Meridian.Agents/Meridian.Agents.csproj", "src/Meridian.Agents/"]
COPY ["src/Meridian.Jobs/Meridian.Jobs.csproj", "src/Meridian.Jobs/"]
RUN dotnet restore "src/Meridian.Api/Meridian.Api.csproj"

COPY . .
WORKDIR "/src/src/Meridian.Api"
RUN dotnet publish -c Release -o /app/publish /p:UseAppHost=false

FROM base AS final
WORKDIR /app
COPY --from=build /app/publish .
ENTRYPOINT ["dotnet", "Meridian.Api.dll"]
