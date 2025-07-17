# Gig Economy Platform - Gig Nepal

A comprehensive Django-based gig economy platform that connects freelancers with clients, featuring job posting, proposal management, contract handling, payment processing, and dispute resolution.

## 🚀 Features

### Core Functionality
- **User Management**: Separate dashboards for freelancers, clients, and admins
- **Job Posting**: Clients can post jobs with detailed requirements and budgets
- **Proposal System**: Freelancers can submit proposals with bids and cover letters
- **Contract Management**: Automated contract creation and management
- **Payment System**: Escrow-based payment processing with wallet functionality
- **Dispute Resolution**: Built-in dispute handling system for admins
- **Messaging System**: Real-time messaging between contract parties
- **Review System**: Rating and review system for completed jobs

### Admin Features
- **Admin Dashboard**: Comprehensive overview of platform statistics
- **User Management**: Ban/unban users, manage user roles
- **Dispute Management**: Handle and resolve disputes
- **Job Management**: Monitor and manage all jobs on the platform
- **Payment Monitoring**: Track all transactions and payments

### Security Features
- **Escrow Payments**: Secure payment holding until job completion
- **User Verification**: Role-based access control
- **Dispute Protection**: Fair dispute resolution system
- **Admin Oversight**: Complete admin control over platform operations

## 🛠️ Technology Stack

- **Backend**: Django 5.1.6
- **Database**: SQLite (development) / PostgreSQL (production ready)
- **Frontend**: HTML, CSS, JavaScript
- **Payment**: Custom wallet system with escrow functionality
- **File Upload**: Django's built-in file handling
- **Authentication**: Django's built-in user authentication

## 📋 Prerequisites

- Python 3.8+
- pip (Python package installer)
- Git

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <your-repository-url>
   cd summer-project
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Main site: http://127.0.0.1:8000/
   - Admin panel: http://127.0.0.1:8000/admin/

## 📁 Project Structure

```
summer-project/
├── core/                   # Core app with base templates and views
├── jobs/                   # Job posting and management
├── users/                  # User management and authentication
├── payments/               # Payment and wallet system
├── gig_economy_system/     # Main Django project settings
├── media/                  # User uploaded files
├── static/                 # Static files (CSS, JS, images)
├── templates/              # HTML templates
├── manage.py              # Django management script
└── requirements.txt       # Python dependencies
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file in the project root with the following variables:
```
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///db.sqlite3
```

### Database Configuration
The project uses SQLite by default. For production, update the database settings in `gig_economy_system/settings.py`.

## 👥 User Roles

### Client
- Post jobs with detailed requirements
- Review and approve proposals
- Manage contracts and payments
- Confirm job completion

### Freelancer
- Browse available jobs
- Submit proposals with bids
- Work on approved contracts
- Mark jobs as completed

### Admin
- Monitor platform activity
- Manage users and disputes
- Oversee payments and contracts
- Platform maintenance

## 💰 Payment System

The platform uses an escrow-based payment system:
1. Client adds funds to their wallet
2. When approving a proposal, funds are deducted and held in escrow
3. Freelancer's pending balance is updated
4. Upon job completion confirmation, funds are released to freelancer

## 🔒 Security Features

- **Role-based Access Control**: Different permissions for different user types
- **Escrow Payments**: Secure payment holding
- **Input Validation**: Comprehensive form validation
- **File Upload Security**: Secure file handling
- **Admin Oversight**: Complete admin control

## 🚀 Deployment

### Production Setup
1. Set `DEBUG=False` in settings
2. Configure a production database (PostgreSQL recommended)
3. Set up static file serving
4. Configure environment variables
5. Set up a web server (Nginx + Gunicorn recommended)

### Docker Deployment (Optional)
```bash
# Build the Docker image
docker build -t gig-economy-platform .

# Run the container
docker run -p 8000:8000 gig-economy-platform
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue in the GitHub repository
- Contact the development team

## 🔄 Version History

- **v1.0.0** - Initial release with core functionality
- **v1.1.0** - Added payment system and escrow functionality
- **v1.2.0** - Enhanced admin panel and dispute resolution
- **v1.3.0** - Improved UI/UX and added messaging system

## 📊 Project Status

- ✅ Core functionality implemented
- ✅ Payment system with escrow
- ✅ Admin panel with full control
- ✅ Dispute resolution system
- ✅ Messaging system
- ✅ User management
- 🔄 Continuous improvements and bug fixes

---

**Developed with ❤️ for the gig economy community** 