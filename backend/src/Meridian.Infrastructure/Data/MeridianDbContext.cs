using Meridian.Core.Entities;
using Microsoft.EntityFrameworkCore;

namespace Meridian.Infrastructure.Data;

public class MeridianDbContext : DbContext
{
    public MeridianDbContext(DbContextOptions<MeridianDbContext> options) : base(options)
    {
    }

    public DbSet<User> Users => Set<User>();
    public DbSet<Trade> Trades => Set<Trade>();
    public DbSet<Strategy> Strategies => Set<Strategy>();
    public DbSet<TradeStrategyTag> TradeStrategyTags => Set<TradeStrategyTag>();
    public DbSet<TradeScreenshot> TradeScreenshots => Set<TradeScreenshot>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        base.OnModelCreating(modelBuilder);

        // User
        modelBuilder.Entity<User>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.HasIndex(e => e.AzureAdB2CId).IsUnique();
            entity.HasIndex(e => e.Email).IsUnique();
            entity.Property(e => e.Email).HasMaxLength(256);
            entity.Property(e => e.AzureAdB2CId).HasMaxLength(128);
            entity.Property(e => e.DisplayName).HasMaxLength(256);
            entity.Property(e => e.StripeCustomerId).HasMaxLength(256);
        });

        // Trade
        modelBuilder.Entity<Trade>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.HasIndex(e => new { e.UserId, e.Status });
            entity.HasIndex(e => new { e.UserId, e.EntryDate });
            entity.Property(e => e.Ticker).HasMaxLength(20);
            entity.Property(e => e.EntryPrice).HasPrecision(18, 4);
            entity.Property(e => e.ExitPrice).HasPrecision(18, 4);
            entity.Property(e => e.PositionSize).HasPrecision(18, 4);
            entity.Property(e => e.StopLoss).HasPrecision(18, 4);
            entity.Property(e => e.TakeProfit).HasPrecision(18, 4);
            entity.Property(e => e.Pnl).HasPrecision(18, 4);
            entity.Property(e => e.PnlPercent).HasPrecision(18, 4);
            entity.Property(e => e.Thesis).HasMaxLength(2000);
            entity.Property(e => e.EmotionalState).HasMaxLength(100);
            entity.Property(e => e.MarketConditions).HasMaxLength(500);
            entity.Property(e => e.Notes).HasMaxLength(5000);

            entity.HasOne(e => e.User)
                .WithMany(u => u.Trades)
                .HasForeignKey(e => e.UserId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        // Strategy
        modelBuilder.Entity<Strategy>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.HasIndex(e => new { e.UserId, e.Name }).IsUnique();
            entity.Property(e => e.Name).HasMaxLength(100);
            entity.Property(e => e.Description).HasMaxLength(500);
            entity.Property(e => e.Source).HasMaxLength(10);

            entity.HasOne(e => e.User)
                .WithMany(u => u.Strategies)
                .HasForeignKey(e => e.UserId)
                .OnDelete(DeleteBehavior.Cascade);
        });

        // TradeStrategyTag (many-to-many join)
        modelBuilder.Entity<TradeStrategyTag>(entity =>
        {
            entity.HasKey(e => new { e.TradeId, e.StrategyId });
            entity.Property(e => e.Source).HasMaxLength(10);

            entity.HasOne(e => e.Trade)
                .WithMany(t => t.StrategyTags)
                .HasForeignKey(e => e.TradeId)
                .OnDelete(DeleteBehavior.Cascade);

            entity.HasOne(e => e.Strategy)
                .WithMany(s => s.TradeStrategyTags)
                .HasForeignKey(e => e.StrategyId)
                .OnDelete(DeleteBehavior.NoAction);
        });

        // TradeScreenshot
        modelBuilder.Entity<TradeScreenshot>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.Property(e => e.BlobUrl).HasMaxLength(1024);
            entity.Property(e => e.Caption).HasMaxLength(500);

            entity.HasOne(e => e.Trade)
                .WithMany(t => t.Screenshots)
                .HasForeignKey(e => e.TradeId)
                .OnDelete(DeleteBehavior.Cascade);
        });
    }
}
