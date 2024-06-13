from models import UserProject


def add_participant(self, user):
    if len(self.participants) < self.participants_needed:
        new_participant = UserProject(user_id=user.id, project_id=self.id)
        self.participants.append(new_participant)
    else:
        raise ValueError("Cannot add more participants, the project is full.")


def remove_participant(self, user):
    for participant in self.participants:
        if participant.user_id == user.id:
            self.participants.remove(participant)
            return
    raise ValueError("User is not a participant of this project.")
