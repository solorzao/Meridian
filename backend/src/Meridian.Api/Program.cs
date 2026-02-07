using Meridian.Agents;
using Meridian.Api.Middleware;
using Meridian.Infrastructure;
using Meridian.Jobs.Configuration;

var builder = WebApplication.CreateBuilder(args);

// Add services
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Add infrastructure (EF, repos, Cosmos, HTTP clients)
builder.Services.AddInfrastructure(builder.Configuration);

// Add Semantic Kernel agents
builder.Services.AddAgents(builder.Configuration);

// Add Hangfire background jobs
builder.Services.AddHangfireJobs(builder.Configuration);

// Add rate limiting
builder.Services.AddRateLimiting();

// CORS
builder.Services.AddCors(options =>
{
    options.AddDefaultPolicy(policy =>
    {
        policy.AllowAnyOrigin()
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

var app = builder.Build();

// Configure pipeline
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseCors();
app.UseErrorHandling();
app.UseRateLimiter();
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();

app.MapGet("/health", () => Results.Ok(new { status = "healthy", service = "meridian-api" }));

app.Run();
